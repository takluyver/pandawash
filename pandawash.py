"""Magic commands to clean up pandas series.

These commands don't act by themselves, but rather create template cleanup
code which the user modifies.
"""
from IPython.core.error import UsageError
from IPython.core.magic import (Magics, magics_class, line_magic)

@magics_class
class DataCleanupMagics(Magics):

    def _addcode(self, code):
        """Shorthand for self.shell.set_next_input"""
        self.shell.set_next_input(code)

    @line_magic
    def groupcol(self, line):
        """Fix inconsistent category names in a column.
        
        Usage::
        
            %groupcol series
        
        This creates a new cell which calls :meth:`pandas.Series.map`.
        Initially all the values are mapped to themselves, producing no change.
        The user should modify this code to replace mistyped values.
        """
        template = ("# Modify the mapping below to group equivalent values\n"
                    "{series} = {series}.map({{\n"
                    "  {fieldmap}\n"
                    "}})")
        series = eval(line, self.shell.user_ns)
        values = sorted(set(series))
        fieldmap = '\n  '.join("{0!r}: {0!r},".format(v) for v in values)
        self._addcode(template.format(series=line, fieldmap=fieldmap))
    
    @line_magic
    def numbercol(self, line):
        """Convert a column to numbers, replacing problematic values.
        
        Usage::
        
            %numbercol series dtype
        
        dtype should be ``int`` or ``float``.
        
        This creates a new cell which allows the user to replace any values
        that can't be converted, and then convert the column to the requested
        type.
        """
        template = ("# Fill in the replacements below\n"
                    "{series} = {series}\\\n"
                    "  {replacements}\n"
                    "  .astype({type})")
        seriesexpr, numtype = line.rsplit(None, 1)
        if numtype not in {'float', 'int'}:
            raise UsageError("Second argument should be 'float' or 'int'.")
        numconv = float if numtype=='float' else int
        series = eval(seriesexpr, self.shell.user_ns)

        replace_lines = []
        if series.isnull().any() and (numconv is int):
            replace_lines.append("  .fillna(value=0)\\")
        for val in set(series.dropna()):
            try:
                numconv(val)
            except ValueError:
                replace_lines.append("  .replace({!r}, '')\\".format(val))

        self._addcode(template.format(series=seriesexpr,
                                      replacements="\n  ".join(replace_lines),
                                      type=numtype))

    @line_magic
    def regexcol(self, line):
        """Check a column using a regex.
        
        Usage::
        
            %regexcol series pattern
        
        If any values don't match the pattern, a cell will be inserted to
        replace them.
        """
        template = ("# Fill in the replacements below\n"
                    "{series} = {series}\\\n"
                    "  {replacements}")
        seriesexpr, pat = line.rsplit(None, 1)
        series = eval(seriesexpr, self.shell.user_ns)

        matched = series.str.match(pat, as_indexer=True)
        if matched.all():
            print("All the values match the pattern; nothing to do.")
            return

        replace_lines = []
        for val in series[~matched]:
            replace_lines.append(".replace({0!r}, {0!r})".format(val))

        self._addcode(template.format(series=seriesexpr,
                                      replacements="\\\n  ".join(replace_lines),
                                    ))

    @line_magic
    def boundscheckcol(self, line):
        """Check that values in a numeric column fall within a range.
        
        Usage::
        
            %boundscheckcol series min-max
        
        If any values are outside the range, a cell will be inserted allowing
        you to replace them.
        """
        template = ("# Fill in the replacements below\n"
                    "{series} = {series}\\\n"
                    "  {replacements}")
        seriesexpr, minmax = line.rsplit(None, 1)
        series = eval(seriesexpr, self.shell.user_ns)

        min, max = minmax.split('-')
        matched = (series >= float(min)) & (series <= float(max))
        if matched.all():
            print("All the values are in the range; nothing to do.")
            return

        replace_lines = []
        for val in series[~matched]:
            replace_lines.append(".replace({0!r}, {0!r})".format(val))

        self._addcode(template.format(series=seriesexpr,
                                      replacements="\\\n  ".join(replace_lines),
                                    ))

def load_ipython_extension(ip):
    ip.register_magics(DataCleanupMagics)