"""Human diagnostics: getter safety, session identity and observational drift."""
import unittest

import test_persistence_lifecycle as lifecycle_fixture


class HumanVisualChecks(unittest.TestCase):
    def setUp(self):
        fixture = lifecycle_fixture.LifecycleChecks()
        fixture.setUp()
        self.lua = fixture.lua
        self.lua.execute('''
            nativeDebug=false;lazyCalls=0;reflectionCalls=0;mutationCalls=0
            getDebug=function() return nativeDebug end
            function forbidden() mutationCalls=mutationCalls+1;error('mutation forbidden') end
            function lazy() lazyCalls=lazyCalls+1;error('lazy getter forbidden') end
            function color(r,g,b)
                return {getRedFloat=function() return r end,getGreenFloat=function() return g end,
                    getBlueFloat=function() return b end,getAlphaFloat=function() return 1 end}
            end
            function visual(owner)
                return {skin=2,bodyHair=0,raw={owner=owner,hairModel='Short',beardModel='Goatee',
                    skinColor=color(0.8,0.6,0.5),hairColor=color(0.1,0.2,0.3),beardColor=color(0.1,0.2,0.3),
                    naturalHairColor=color(0.1,0.2,0.3),naturalBeardColor=color(0.1,0.2,0.3)},
                    getSkinTextureIndex=function(self) return self.skin end,
                    getBodyHairIndex=function(self) return self.bodyHair end,
                    getNonAttachedHair=function() return nil end,
                    getHairModel=lazy,getBeardModel=lazy,getSkinTexture=lazy,getSkinColor=lazy,
                    getHairColor=lazy,getBeardColor=lazy,getNaturalHairColor=lazy,getNaturalBeardColor=lazy}
            end
            descriptor={getID=function() return 12 end,getForename=function() return 'Bob' end,
                getSurname=function() return 'Human' end,isFemale=function() return false end}
            humanVisual=visual(player);descriptorVisual=visual(descriptor)
            descriptor.getHumanVisual=function() return descriptorVisual end
            player.getDescriptor=function() return descriptor end
            player.getHumanVisual=function() return humanVisual end
            player.isFemale=function() return false end;player.getPlayerNum=function() return 0 end
            player.flags={invisible=false,alpha=1}
            player.isInvisible=function() return player.flags.invisible end
            player.isGhostMode=player.isInvisible
            player.isGodMod=function() return false end;player.isNoClip=function() return false end
            player.isSpriteInvisible=function() return false end;player.isSceneCulled=function() return false end
            player.getDoRender=function() return true end
            player.getAlpha=function() return player.flags.alpha end;player.getTargetAlpha=player.getAlpha
            model={raw={model={raw={name='MaleBody'}},tintR=1,tintG=1,tintB=1}}
            creator={}
            player.getModelInstance=function() return model end
            player.getTextureCreator=function() return creator end
            player.getAnimationPlayer=forbidden;player.resetModel=forbidden
            player.setInvisible=forbidden;player.setGhostMode=forbidden;player.setGodMod=forbidden
            getNumClassFields=function(o)
                assert(nativeDebug);reflectionCalls=reflectionCalls+1
                return 15
            end
            local fieldNames={'owner','skinTextureName','hairModel','beardModel','skinColor','hairColor','beardColor',
                'naturalHairColor','naturalBeardColor','model','name','tintR','tintG','tintB','absent'}
            getClassField=function(_,i) return {getName=function() return fieldNames[i+1] end} end
            getClassFieldVal=function(o,field) return o.raw and o.raw[field:getName()] end
            Perks.Strength='Strength';Perks.Fitness='Fitness';CharacterStat.ENDURANCE='endurance'
            require 'Testing/SSRHumanVisualTest'
            H=SSRHumanVisualDiagnostics
            function humanRun(id)
                clock=clock+100;return run(id)
            end
            function baseline() return humanRun('human-visual-baseline') end
            function changed() return humanRun('human-visual-changed') end
            function invisible() return humanRun('human-visual-invisible') end
            function clean() assert(lazyCalls==0 and mutationCalls==0 and slots[0]==player and singleton==player) end
        ''')

    def test_no_auto_capture_or_world_manifest_write_and_five_visible_entries(self):
        self.lua.execute('''
            assert(#SSRTests.list()==5 and not H.baseline)
            fire('OnTick');fire('OnTick');assert(not H.baseline)
            assert(not ModData.get('SSR.Tests.HumanVisual'))
            assert(#allActors==1 and lazyCalls==0 and reflectionCalls==0);clean()
        ''')

    def test_read_only_capture_does_not_draw_gameplay_rng_or_create_boot_token(self):
        self.lua.execute('''
            ZombRand=function() error('RNG draw forbidden for read-only control') end
            baseline();assert(not SSRTests.bootToken);changed();clean()
        ''')

    def test_baseline_without_debug_skips_mutating_getters_and_reports_missing_fields(self):
        self.lua.execute('''
            local result=baseline();assert(result.status=='PASSED')
            local f=H.baseline.fields
            assert(f['visual.actor.skinTextureIndex'].value==2)
            assert(not f['visual.actor.hairModel'].available and not f['visual.actor.hairColor'].available)
            assert(reflectionCalls==0 and f['visibility.isInvisible'].value==false)
            for _,entry in pairs(f) do
                assert(type(entry)=='table' and (not entry.available or type(entry.value)~='table'))
            end
            clean()
        ''')

    def test_read_only_capture_can_preserve_symptom_after_prior_cleanup_failure(self):
        self.lua.execute('''
            local failure={};SSRTests.cleanupFailure=failure
            assert(not SSRTests.start('human-visual-baseline',false)) -- Consent still required.
            baseline();changed()
            assert(SSRTests.cleanupFailure==failure)
            assert(not SSRTests.start('ssr-restart-stage',true));clean()
        ''')

    def test_debug_raw_style_colors_and_known_null_do_not_initialize_appearance(self):
        self.lua.execute('''
            nativeDebug=true;humanVisual.raw.beardModel=nil
            baseline();local f=H.baseline.fields
            assert(f['visual.actor.hairModel'].value=='Short')
            assert(f['visual.actor.hairColor'].value=='0.100000,0.200000,0.300000,1.000000')
            assert(f['visual.actor.beardModel'].available and f['visual.actor.beardModel'].kind=='null')
            assert(f['visual.actor.ownerMatches'].value==true and reflectionCalls>0)
            clean()
        ''')

    def test_dynamic_xp_inventory_equipment_and_position_are_context_not_failures(self):
        self.lua.execute('''
            baseline();local old=H.baseline
            player.payload.axeXP=88;player.payload.x=9
            local item=player:getInventory():AddItem('Base.NewItem');player:setPrimaryHandItem(item)
            local result=changed()
            assert(result.status~='FAILED' and result.observations.sameActor)
            assert(result.observations.changes.context>0 and result.observations.changes.visual==0)
            assert(H.baseline==old and H.baseline.fields['context.xp.Axe'].value==0)
            clean()
        ''')

    def test_visual_data_change_preserves_baseline_and_separate_history(self):
        self.lua.execute('''
            nativeDebug=true;baseline();local old=H.baseline
            humanVisual.skin=5;humanVisual.raw.hairModel='Long'
            local result=changed()
            assert(result.status=='INCONCLUSIVE' and result.observations.changes.visual>=2)
            assert(H.baseline==old and old.fields['visual.actor.hairModel'].value=='Short')
            assert(H.history[1].fields['visual.actor.hairModel'].value=='Long');clean()
        ''')

    def test_invisible_flag_changed_is_recorded_without_toggle_or_reset(self):
        self.lua.execute('''
            baseline();player.flags.invisible=true;player.flags.alpha=0
            local result=invisible()
            assert(result.observations.currentInvisible.available and result.observations.currentInvisible.value==true)
            assert(result.observations.changes.visibility>=3 and player.flags.invisible)
            assert(table.concat(result.lines,' | '):find('CURRENT isInvisible=true',1,true))
            clean()
        ''')

    def test_unchanged_data_with_reported_symptom_does_not_claim_renderer_correct(self):
        self.lua.execute('''
            nativeDebug=true;baseline();local result=changed()
            assert(result.observations.changes.visual==0 and result.observations.changes.visibility==0)
            assert(result.status=='INCONCLUSIVE')
            assert(result.summary:find('unavailable',1,true));clean()
        ''')

    def test_missing_baseline_and_other_world_are_blocked(self):
        self.lua.execute('''
            assert(not SSRTests.start('human-visual-changed',true))
            baseline();local old=H.baseline
            world='B';assert(not SSRTests.start('human-visual-invisible',true))
            assert(H.baseline==old);clean()
        ''')

    def test_intentional_new_human_actor_is_not_compared_as_original_human(self):
        self.lua.execute('''
            baseline();local old=H.baseline
            local other=actor(2,2,0,true);slots[0]=other;singleton=other
            local result=changed()
            assert(result.status=='INCONCLUSIVE' and not result.observations.sameActor)
            assert(not result.observations.changes and H.baseline==old)
            assert(table.concat(result.lines,' | '):find('IDENTITY CHANGE:',1,true))
            assert(mutationCalls==0 and lazyCalls==0)
        ''')

    def test_changed_slot_or_singleton_is_reported_without_restoration(self):
        self.lua.execute('''
            baseline();local other=actor(3,3,0,true)
            slots[1]=other;local first=changed()
            assert(not first.observations.slotsUnchanged and first.status=='INCONCLUSIVE')
            assert(slots[1]==other)
            slots[1]=nil;singleton=other;local second=changed()
            assert(second.status=='INCONCLUSIVE' and singleton==other and mutationCalls==0)
        ''')

    def test_replaced_visual_handle_is_reported_even_when_readable_data_matches(self):
        self.lua.execute('''
            nativeDebug=true;baseline();humanVisual=visual(player)
            local result=changed()
            assert(result.observations.referenceChanges>0 and result.observations.changes.visual==0)
            assert(result.status=='INCONCLUSIVE');clean()
        ''')

    def test_null_visual_and_missing_reflection_remain_unavailable_not_equal(self):
        self.lua.execute('''
            humanVisual=nil;descriptorVisual=nil;nativeDebug=true;getClassFieldVal=nil
            baseline();local result=invisible()
            assert(result.status=='INCONCLUSIVE' and result.observations.changes.unavailable>0)
            assert(not H.baseline.fields['visual.actor.skinTextureIndex'].available)
            assert(H.baseline.fields['visual.actor.present'].value==false);clean()
        ''')

    def test_missing_getter_is_unavailable_not_known_absent(self):
        self.lua.execute('''
            player.getHumanVisual=nil;player.getModelInstance=nil
            baseline();local f=H.baseline.fields
            assert(not f['visual.actor.present'].available)
            assert(not f['render.modelInstancePresent'].available)
            local result=changed();assert(result.observations.changes.unavailable>0);clean()
        ''')

    def test_history_is_bounded_and_new_session_requires_new_baseline(self):
        self.lua.execute('''
            baseline();local stamp=H.baseline.time
            for i=1,7 do changed() end
            assert(#H.history==4 and H.baseline.time==stamp)
            local captures=reflectionCalls;fire('OnGameStart')
            assert(not H.baseline and #H.history==0 and reflectionCalls==captures)
            assert(not SSRTests.start('human-visual-changed',true));clean()
        ''')


if __name__ == '__main__':
    unittest.main()
