"""Clone fingerprints preserve literals, ignore comments and extend real matches."""
import importlib.util
from pathlib import Path
import sys
import unittest

spec = importlib.util.spec_from_file_location('lua_clones', Path(__file__).resolve().parents[1] / 'tools/find_lua_clones.py')
clones = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = clones
spec.loader.exec_module(clones)


def source(name, text):
    tokens, structural, lines = clones.tokenize(text)
    return clones.Source(name, tokens, structural, lines, clones.function_spans(tokens), '')


class LuaCloneChecks(unittest.TestCase):
    def test_comments_do_not_hide_strings_or_change_line_numbers(self):
        values, _, lines = clones.tokenize('--[=[ multi\nline ]=]\nlocal text = "--real string"; -- comment\nreturn text')
        self.assertEqual(values, ['local', 'text', '=', '"--real string"', 'return', 'text'])
        self.assertEqual(lines, [3, 3, 3, 3, 4, 4])

    def test_structural_pass_masks_variables_but_keeps_calls_fields_and_literals(self):
        a = source('a', 'local x = getPlayer(); x:walkTo(3, "Guard")')
        b = source('b', 'local buddy = getPlayer(); buddy:walkTo(3, "Guard")')
        self.assertNotEqual(a.values,b.values)
        self.assertEqual(a.structural,b.structural)
        self.assertNotEqual(a.structural,source('c','local x=getPlayer();x:attack(3,"Guard")').structural)
        self.assertNotEqual(a.structural,source('c','local x=getPlayer();x:walkTo(4,"Guard")').structural)

    def test_scan_extends_tokens_and_does_not_report_nonmatching_hash_seeds(self):
        a = source('a', 'local x = 1\nx = x + 2\nprint(x)')
        b = source('b', '-- different formatting\nlocal x=1; x=x+2; print(x)')
        rows, _ = clones.scan([a,b], [], 'exact', minimum=8, min_lines=1, width=4)
        self.assertTrue(any(r['tokens']==len(a.values) for r in rows))
        rows, _ = clones.scan([a,source('c','local x=9\nx=x-4\nprint("different")')], [], 'exact', minimum=8,min_lines=1,width=4)
        self.assertFalse(rows)

    def test_function_recognizer_handles_loops_and_nested_conditionals(self):
        doc = source('a','function One(a) for i=1,3 do if a then a=a+1 end end return a end\nfunction Two(a) for i=1,3 do if a then a=a+1 end end return a end')
        self.assertEqual(len(doc.functions),2)
        self.assertEqual(len(clones.short_functions([doc])),1)

    def test_same_file_nonoverlapping_repeated_block_is_found(self):
        doc = source('a','local x=1\nx=x+2\nprint(x)\nlocal different=7\nlocal x=1\nx=x+2\nprint(x)')
        rows,_ = clones.scan([doc],[],'exact',minimum=8,min_lines=2,width=4)
        self.assertTrue(rows)

    def test_pruning_does_not_discard_exact_evidence_inside_structural_match(self):
        def row(mode,start,end,size):
            return {'mode':mode,'tokens':size,'a':{'file':'a','start':start,'end':end},'b':{'file':'b','start':start,'end':end}}
        self.assertEqual(len(clones.prune([row('exact',2,3,20),row('structural',1,4,30)])),2)
