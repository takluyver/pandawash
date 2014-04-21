"""Magic commands to clean up pandas series.

These commands don't act by themselves, but rather create template cleanup
code which the user modifies.
"""
from IPython.core.error import UsageError
from IPython.core.magic import (Magics, magics_class, line_magic)

@magics_class
class DataCleanupMagics(Magics):
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
        self.shell.set_next_input(template.format(series=line, fieldmap=fieldmap))
    
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
        seriesexpr, numtype = line.rsplit(" ", 1)
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
        
        replacements = "\n  ".join(replace_lines)
        self.shell.set_next_input(template.format(series=seriesexpr,
                                                  replacements=replacements,
                                                  type=numtype))

def load_ipython_extension(ip):
    ip.register_magics(DataCleanupMagics)