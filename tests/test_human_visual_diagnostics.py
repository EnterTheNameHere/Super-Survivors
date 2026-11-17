"""Human diagnostics: safe scalar persistence, identity and observational drift."""
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

    def test_human_controls_do_not_draw_gameplay_rng_or_create_boot_token(self):
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

    def test_read_only_after_can_preserve_symptom_after_prior_cleanup_failure(self):
        self.lua.execute('''
            baseline()
            local failure={};SSRTests.cleanupFailure=failure
            assert(not SSRTests.start('human-visual-baseline',false)) -- Consent still required.
            assert(not SSRTests.start('human-visual-baseline',true)) -- Metadata capture is a write.
            changed()
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

    def test_history_is_bounded_and_new_session_can_read_saved_baseline(self):
        self.lua.execute('''
            baseline();local stamp=H.baseline.time
            for i=1,7 do changed() end
            assert(#H.history==4 and H.baseline.time==stamp)
            local captures=reflectionCalls;fire('OnGameStart')
            assert(not H.baseline and #H.history==0 and reflectionCalls==captures)
            local result=changed()
            assert(H.baseline.time==stamp and H.baseline.crossSession)
            assert(result.observations.crossSession and result.status=='INCONCLUSIVE');clean()
        ''')

    def test_saved_record_has_only_scalars_and_no_reference_aliases(self):
        self.lua.execute('''
            baseline();local record=ModData.get(H.KEY).baseline
            assert(record.schema==1 and not record.refs and record.fields~=H.baseline.fields)
            local function safe(t,depth)
                assert(depth<5 and not getmetatable(t))
                for k,v in pairs(t) do
                    assert(type(k)=='string')
                    if type(v)=='table' then safe(v,depth+1)
                    else assert(type(v)=='number' or type(v)=='string' or type(v)=='boolean') end
                end
            end
            safe(record,0)
            H.baseline.fields['identity.forename'].value='Only memory'
            assert(record.fields['identity.forename'].value=='Bob');clean()
        ''')

    def test_no_save_mode_and_no_data_do_not_create_a_diagnostic_record(self):
        self.lua.execute('''
            local core=getCore();core.isNoSave=function() return true end
            getCore=function() return core end
            local ok,why=SSRTests.availability(SSRTests.definitions['human-visual-baseline'])
            assert(not ok and why:find('Saving is disabled',1,true))
            assert(not SSRTests.start('human-visual-baseline',true))
            fire('OnGameStart');fire('OnSave')
            assert(not ModData.get(H.KEY) and not H.baseline);clean()
        ''')

    def test_on_save_event_without_completed_native_write_does_not_make_capture_durable(self):
        self.lua.execute('''
            disk=copy(worlds.A.tables);baseline()
            fire('OnSave') -- callback alone is not proof native GlobalModData write completed
            restart()
            assert(not SSRTests.start('human-visual-changed',true))
            assert(not ModData.get(H.KEY));clean()
        ''')

    def test_reloaded_baseline_keeps_strong_checks_from_first_explicit_after_this_session(self):
        self.lua.execute('''
            baseline();saveGame();restart();changed()
            humanVisual=visual(player)
            local swapped=invisible()
            assert(swapped.observations.referenceChanges>0 and swapped.observations.sessionReferencesChecked)
            local other=actor(3,3,0,true)
            other.getDescriptor=function() return descriptor end
            slots[0]=other;singleton=other
            local result=changed()
            assert(not result.observations.sessionActorUnchanged and not result.observations.changes)
            assert(result.summary:find('Same-session actor/slot/singleton changed',1,true))
            assert(not result.observations.crossSessionIdentityVerified)
            assert(lazyCalls==0 and mutationCalls==0)
        ''')

    def test_completed_normal_save_restores_baseline_and_skips_cross_session_references(self):
        self.lua.execute('''
            baseline();local stamp=H.baseline.time
            saveGame();restart()
            humanVisual=visual(player);model={};descriptorVisual=visual(descriptor)
            local before=copy(ModData.get(H.KEY))
            local first=changed();local second=invisible()
            assert(#eventErrors==0 and first.status=='INCONCLUSIVE')
            assert(first.observations.crossSession and first.observations.sameActor==nil)
            assert(first.observations.slotsUnchanged==nil and first.observations.referenceChanges==0)
            assert(first.observations.baselineTimestamp==stamp and first.observations.hintsMatch)
            local log=table.concat(first.lines,' | ')
            assert(log:find('CROSS-SESSION identity UNVERIFIED',1,true))
            assert(not log:find('reference unchanged=',1,true))
            assert(H.baseline.time==stamp and ModData.get(H.KEY).baseline.time==stamp)
            assert(H.history[1].crossSession and H.history[1].sameActor==nil)
            assert(ModData.get(H.KEY).baseline.fields['visual.actor.skinTextureIndex'].value==before.baseline.fields['visual.actor.skinTextureIndex'].value)
            assert(second.observations.baselineTimestamp==stamp);clean()
        ''')

    def test_capture_without_completed_save_is_lost_and_old_saved_baseline_survives(self):
        self.lua.execute('''
            disk=copy(worlds.A.tables)
            baseline();restart()
            assert(not SSRTests.start('human-visual-changed',true))
            assert(not ModData.get(H.KEY))
            baseline();saveGame();local saved=H.baseline.time
            baseline();assert(H.baseline.time~=saved)
            restart();changed();assert(H.baseline.time==saved);clean()
        ''')

    def test_startup_and_afters_never_create_or_write_moddata_or_force_save(self):
        self.lua.execute('''
            baseline();saveGame();restart()
            local old=ModData.get(H.KEY).baseline
            ModData.getOrCreate=function() error('AFTER write forbidden') end
            player.save=forbidden;player.load=forbidden
            changed();invisible();changed()
            assert(ModData.get(H.KEY).baseline==old)
            assert(not H.baseline.refs and #H.history==3);clean()
        ''')

    def test_wrong_world_record_is_rejected_without_overwrite(self):
        self.lua.execute('''
            baseline();local root=copy(ModData.get(H.KEY))
            world='B';worlds.B.tables[H.KEY]=root;fire('OnGameStart')
            local ok,why=SSRTests.availability(SSRTests.definitions['human-visual-changed'])
            assert(not ok and why:find('another save world',1,true))
            assert(worlds.B.tables[H.KEY]==root and not H.baseline);clean()
        ''')

    def test_new_human_hints_prevent_comparison_and_names_never_prove_identity(self):
        self.lua.execute('''
            baseline();saveGame();restart()
            descriptor.getForename=function() return 'New human' end
            local result=changed()
            assert(result.status=='INCONCLUSIVE' and not result.observations.changes)
            assert(not result.observations.crossSessionIdentityVerified)
            assert(result.summary:find('comparison withheld',1,true))
            descriptor.getForename=function() return 'Bob' end
            local matching=changed()
            assert(matching.observations.hintsMatch and not matching.observations.crossSessionIdentityVerified)
            assert(matching.status=='INCONCLUSIVE');clean()
        ''')

    def test_stale_corrupt_and_nonscalar_records_rejected_without_repair(self):
        self.lua.execute('''
            baseline();local good=copy(ModData.get(H.KEY).baseline)
            local mutations={
                function(r) r.schema=99 end,
                function(r) r.engine='41' end,
                function(r) r.time={} end,
                function(r) r.fields={} end,
                function(r) r.fields['identity.forename'].value={} end,
                function(r) r.fields['identity.forename'].kind='number' end,
                function(r) r.fields['visibility.isInvisible'].value=0/0 end,
                function(r) r.fields['visual.actor.hairColor'].available=nil end,
                function(r) r.fields['context.x'].value=string.rep('a',3001) end,
                function(r) r.fields['context.x'].extra=function() end end,
                function(r) r.fields['visual.actor.nonAttachedHair'].value='invalid null' end,
                function(r) r.fields['context.x']=r end
            }
            for _,mutate in ipairs(mutations) do
                local bad=copy(good);mutate(bad)
                ModData.get(H.KEY).baseline=bad;fire('OnGameStart')
                local ok,why=SSRTests.availability(SSRTests.definitions['human-visual-changed'])
                assert(not ok and why:find('rejected',1,true),why)
                assert(ModData.get(H.KEY).baseline==bad and not H.baseline)
            end
            baseline();assert(ModData.get(H.KEY).baseline.schema==1);clean()
        ''')

    def test_reloaded_unavailable_debug_fields_stay_unavailable_when_debug_changes(self):
        self.lua.execute('''
            baseline();saveGame();restart();nativeDebug=true
            local result=changed()
            local entry=H.baseline.fields['visual.actor.hairColor']
            assert(not entry.available and result.observations.changes.unavailable>0)
            assert(H.history[1].fields['visual.actor.hairColor'].available)
            local log=table.concat(result.lines,' | ')
            assert(log:find('UNAVAILABLE visual.actor.hairColor: baseline=UNAVAILABLE',1,true))
            assert(log:find('current=0.100000',1,true));clean()
        ''')


if __name__ == '__main__':
    unittest.main()
