from nipype.interfaces.workbench import base as wb
from nipype.interfaces.base import BaseInterface, BaseInterfaceInputSpec, File, Str, isdefined, TraitedSpec, CommandLineInputSpec
from traits.api import List

# another quick and dirty implementation
# note that cifti needs an input in the -cifti <index> <name> format
# try passing inputs it into a function that reformats lists like so
# newList = [' '.join([str(i),item]) for i,item in enumerate(oldList)]
class SetMapNamesInputSpec(CommandLineInputSpec):
    in_file=File(
        argstr='%s',
        position=0,
        genfile=True,
        desc="The file to se tthe map names of."
    )

    map=List(Str(),
        desc='specify an input cifti file list',
        argstr='-map %s...',
        mandatory=True,
        position=1)

class SetMapNamesOutputSpec(TraitedSpec):
    out_file=File(
        exists=True,
        desc="the input cifti file"
    )

class SetMapNames(wb.WBCommand):
    input_spec = SetMapNamesInputSpec
    output_spec = SetMapNamesOutputSpec

    _cmd = 'wb_command -set-map-names'

    def _gen_filename(self, name):
        import os

        if name == 'out_file':
            if 'out_file' not in self.inputs.get() or not isdefined(self.inputs.out_file):
                return self.inputs.in_file
            return self.inputs.out_file

    def _list_outputs(self):
        outputs = self.output_spec().get()
        if 'out_file' not in outputs or not isdefined(outputs['out_file']):
            outputs['out_file'] = self._gen_filename('out_file')

        return outputs
