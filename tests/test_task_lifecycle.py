"""Regression checks for active/queued cancellation and multi-update patrols."""
from pathlib import Path
import unittest
from lupa.lua51 import LuaRuntime

CLIENT = Path(__file__).resolve().parents[1] / '42/media/lua/client'


class TaskLifecycleChecks(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute((CLIENT / '7_Tasks/TaskManager.lua').read_bytes())
        self.lua.execute('''
            function AIManager(tm) return tm end
            function task(name)
                return {Name=name,isComplete=function() return false end,update=function() end}
            end
            tm=TaskManager:new({}); calls={}
        ''')

    def test_clear_cleans_active_and_all_queued_tasks_without_retained_entries(self):
        self.lua.execute('''
            for i=1,3 do
                local t=task(tostring(i))
                t.ForceComplete=function() table.insert(calls,i); assert(tm.TaskCount==0) end
                tm:AddToBottom(t)
            end
            tm:clear()
            assert(#calls==3 and tm.TaskCount==0 and next(tm.Tasks)==nil)
            tm:clear(); assert(#calls==3)
        ''')

    def test_failed_cleanup_does_not_leave_other_tasks_active(self):
        self.lua.execute('''
            local a,b=task('a'),task('b')
            a.ForceComplete=function() error('cleanup failed') end
            b.ForceFinish=function() cleaned=true end
            tm:AddToBottom(a);tm:AddToBottom(b)
            local ok,reason=pcall(tm.clear,tm)
            assert(not ok and string.find(reason,'cleanup failed') and cleaned)
            assert(tm.TaskCount==0 and next(tm.Tasks)==nil)
        ''')

    def test_named_removal_includes_active_and_compacts_queue(self):
        self.lua.execute('''
            local a,b,c=task('remove'),task('keep'),task('remove')
            a.OnComplete=function() calls[1]=true end
            c.OnCancel=function() calls[2]=true end
            tm:AddToBottom(a);tm:AddToBottom(b);tm:AddToBottom(c)
            assert(tm:getTaskFromName('remove')==a)
            tm:removeTaskFromName('remove')
            assert(tm.TaskCount==1 and tm.Tasks[0]==b and tm.Tasks[1]==nil)
            assert(calls[1] and calls[2] and tm.CurrentTask=='keep')
        ''')

    def test_timeout_cancels_before_promoting_next_task(self):
        self.lua.execute('''
            local a,b=task('a'),task('b')
            a.ForceComplete=function() cleaned=true end
            tm:AddToBottom(a);tm:AddToBottom(b);tm:setTaskUpdateLimit(1)
            tm:update();tm:update()
            assert(cleaned and tm.TaskCount==1 and tm.Tasks[0]==b and tm.Tasks[1]==nil)
        ''')

    def test_normal_completion_calls_completion_once_without_cancellation(self):
        self.lua.execute('''
            local a=task('a');a.isComplete=function() return true end
            a.OnComplete=function() calls[1]=(calls[1] or 0)+1 end
            a.ForceComplete=function() error('wrong lifecycle') end
            tm:AddToTop(a);tm:update();tm:update()
            assert(calls[1]==1 and tm.TaskCount==0)
        ''')

    def test_explicit_tasks_can_run_without_autonomous_ai(self):
        self.lua.execute('''
            function AIManager() error('autonomy must be disabled') end
            local a=task('a');a.update=function() updated=true end
            tm.AIEnabled=false;tm:AddToTop(a);tm:update();assert(updated)
        ''')

    def test_patrol_keeps_destination_until_arrival(self):
        self.lua.execute((CLIENT / '7_Tasks/PatrolTask.lua').read_bytes())
        self.lua.execute('''
            local a,b,mid={},{},{}
            local current=a
            local parent={isInAction=function() return false end,getDangerSeenCount=function() return 0 end,
                player={getCurrentSquare=function() return current end},walkToDirect=function(_,sq) target=sq end}
            local t=setmetatable({parent=parent,Square1=a,Square2=b,NextPoint=1,ArrivalCount=0},PatrolTask)
            t:update();assert(target==b and t.ArrivalCount==1)
            current=mid;t:update();assert(target==b and t.ArrivalCount==1)
            current=b;t:update();assert(target==a and t.ArrivalCount==2)
            current=mid;t:update();assert(target==a)
            current=a;t:update();assert(target==b and t.ArrivalCount==3)
        ''')
