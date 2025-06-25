# connectome workbench interfaces.
# Developer Notes:
# Don't reinvent the wheel. These are not implemented in Nipype but multiple other packages build off this.
# It's worth checking nipreps repos (e.g. fmriprep, smriprep, etc.) to see if they've implemented a workbench
# inteface before implementing your own. Those are also probably better sources for example interfaces
# than my own relatively amateurish attempts here.

from nipype.interfaces.workbench import base as wb
from nipype.interfaces.base import (
    BaseInterface, 
    BaseInterfaceInputSpec, 
    traits, 
    File, 
    isdefined, 
    TraitedSpec, 
    CommandLineInputSpec, 
    Str
)
from traits.api import List

_valid_cifti_structs = ['CORTEX_LEFT',
                        'CORTEX_RIGHT',
                        'CEREBELLUM',
                        'ACCUMBENS_LEFT',
                        'ACCUMBENS_RIGHT',
                        'ALL_GREY_MATTER',
                        'ALL_WHITE_MATTER',
                        'AMYGDALA_LEFT',
                        'AMYGDALA_RIGHT',
                        'BRAIN_STEM',
                        'CAUDATE_LEFT',
                        'CAUDATE_RIGHT',
                        'CEREBELLAR_WHITE_MATTER_LEFT',
                        'CEREBELLAR_WHITE_MATTER_RIGHT',
                        'CEREBELLUM_LEFT',
                        'CEREBELLUM_RIGHT',
                        'CEREBRAL_WHITE_MATTER_LEFT',
                        'CEREBRAL_WHITE_MATTER_RIGHT',
                        'CORTEX',
                        'DIENCEPHALON_VENTRAL_LEFT',
                        'DIENCEPHALON_VENTRAL_RIGHT',
                        'HIPPOCAMPUS_LEFT',
                        'HIPPOCAMPUS_RIGHT',
                        'INVALID',
                        'OTHER',
                        'OTHER_GREY_MATTER',
                        'OTHER_WHITE_MATTER',
                        'PALLIDUM_LEFT',
                        'PALLIDUM_RIGHT',
                        'PUTAMEN_LEFT',
                        'PUTAMEN_RIGHT',
                        'THALAMUS_LEFT',
                        'THALAMUS_RIGHT']
                        
_valid_cifti_units = ['SECOND', 'HERTZ', 'METER', 'RADIAN']

# This was drafted by chatGPT based on CiftiConvertNifti and NiftiConvertCifti (below)
class CiftiConvertTextInputSpec(CommandLineInputSpec):
    to_text = traits.Bool(True,
        argstr="-to-text",
        usedefault=True,
        desc="Convert CIFTI to text")

    in_file = File(
        exists=True,
        argstr="%s",
        position=1,
        mandatory=True,
        desc="Input CIFTI file"
    )

    out_file = File(
        argstr="%s",
        position=2,
        genfile=True,
        desc="Output text file"
    )


class CiftiConvertTextOutputSpec(TraitedSpec):
    out_file = File(
        exists=True,
        desc="Converted text output"
    )


class CiftiConvertText(wb.WBCommand):
    input_spec = CiftiConvertTextInputSpec
    output_spec = CiftiConvertTextOutputSpec

    _cmd = 'wb_command -cifti-convert'

    def _gen_filename(self, name):
        import os
        if name == 'out_file':
            if not isdefined(self.inputs.out_file):
                base, _ = os.path.splitext(os.path.basename(self.inputs.in_file))
                base, _ = os.path.splitext(base)
                return os.path.join(os.getcwd(), base + '.txt')
            return self.inputs.out_file

    def _list_outputs(self):
        outputs = self.output_spec().get()
        outputs['out_file'] = self._gen_filename('out_file')
        return outputs

# convert cifti to nifti and back
# this interface was drafted by ChatGPT then heavily modified by BP.
class CiftiConvertNiftiInputSpec(CommandLineInputSpec):
    to_nifti = traits.Bool(True,
        argstr="-to-nifti",
        position=0,
        usedefault=True,
        desc="Convert to NIFTI")

    cifti_in = File(
        desc="The input CIFTI file",
        exists=True,
        argstr="%s",
        position=1,
        mandatory=True,
        requires=['to_nifti']
    )
    nifti_out = File(
        desc="The output NIFTI file",
        argstr="%s",
        position=2,
        genfile=True,
        requires=['to_nifti']
    )
    smaller_file = traits.Bool(
        desc="Use better-fitting dimension lengths",
        argstr="-smaller-file",
        position=3,
        requires=['to_nifti']
    )
    smaller_dims = traits.Bool(
        desc="Minimize the largest dimension",
        argstr="-smaller-dims",
        position=4,
        requires=['to_nifti']
    )


class CiftiConvertNiftiOutputSpec(TraitedSpec):
    out_file = File(
        desc="The converted file",
        exists=True
    )


class CiftiConvertNifti(wb.WBCommand):
    input_spec = CiftiConvertNiftiInputSpec
    output_spec = CiftiConvertNiftiOutputSpec
    _cmd = 'wb_command -cifti-convert'

    def _check_required_inputs(self):
        """Ensure required inputs are in place based on the conversion direction."""
        super(CiftiConvertNifti, self)._check_required_inputs()
        if not isdefined(self.inputs.cifti_in):
            raise ValueError("cifti_in is required when to_nifti is True")
        if not isdefined(self.inputs.nifti_out):
            self.inputs.nifti_out = self._gen_filename('nifti_out')

    def _list_outputs(self):

        outputs = self.output_spec().get()
        if not isdefined(self.inputs.nifti_out):
            self.inputs.nifti_out = self._gen_filename('nifti_out')
        outputs['out_file'] = self.inputs.nifti_out

        return outputs

    def _gen_filename(self, name):
        import os

        if name == 'nifti_out':
            if not isdefined(self.inputs.nifti_out):
                fname, _ = os.path.splitext(os.path.basename(self.inputs.cifti_in))
                fname, _ = os.path.splitext(fname)
                return os.path.join(os.getcwd(), fname + '.nii')
            return self.inputs.nifti_out


# convert cifti to nifti and back
# this interface was drafted by ChatGPT then heavily modified by BP.
class NiftiConvertCiftiInputSpec(CommandLineInputSpec):
    from_nifti = traits.Bool(True,
        argstr="-from-nifti",
        position=0,
        usedefault=True,
        desc="Convert to NIFTI")

    nifti_in = File(
        desc="The input NIFTI file",
        exists=True,
        argstr="%s",
        position=1,
        mandatory=True,
        requires=['from_nifti']
    )
    cifti_template = File(
        desc="The CIFTI file with the dimension(s) and mapping(s) to be used",
        exists=True,
        argstr="%s",
        position=2,
        requires=['from_nifti']
    )
    cifti_out = File(
        desc="The output CIFTI file",
        argstr="%s",
        position=3,
        genfile=True,
        requires=['from_nifti']
    )
    # reset timepoints would go here if you decide to introduce it
    reset_scalars = traits.Bool(
        desc="reset mapping along rows to scalars, taking length from the nifti file",
        argstr="-reset-scalars",
        position=-1,
        requires=['from_nifti']
    )

class NiftiConvertCiftiOutputSpec(TraitedSpec):
    out_file = File(
        desc="The converted file",
        exists=True
    )

class NiftiConvertCifti(wb.WBCommand):
    input_spec = NiftiConvertCiftiInputSpec
    output_spec = NiftiConvertCiftiOutputSpec
    _cmd = 'wb_command -cifti-convert'

    def _check_required_inputs(self):
        """Ensure required inputs are in place based on the conversion direction."""
        super(CiftiConvertNifti, self)._check_required_inputs()
        if not isdefined(self.inputs.nifti_in):
            raise ValueError("nifti_in is required when from_nifti is True")
        if not isdefined(self.inputs.cifti_template):
            raise ValueError("cifti_template is required when from_nifti is True")
        if not isdefined(self.inputs.cifti_out):
            self.inputs.cifti_out = self._gen_filename('cifti_out')

    def _list_outputs(self):

        outputs = self.output_spec().get()

        if not isdefined(self.inputs.cifti_out):
            self.inputs.cifti_out = self._gen_filename('cifti_out')
        outputs['out_file'] = self.inputs.cifti_out

        return outputs

    def _gen_filename(self, name):
        import os

        if name == 'cifti_out':
            if not isdefined(self.inputs.cifti_out):
                fname, _ = os.path.splitext(os.path.basename(self.inputs.nifti_in))
                fname, _ = os.path.splitext(fname)

                _fname, ext1 = os.path.splitext(os.path.basename(self.inputs.cifti_template))
                _, ext2 = os.path.splitext(_fname)

                if self.inputs.reset_scalars:
                    ext2 = '.dscalar'

                return os.path.join(os.getcwd(), fname + ext2 + ext1)
            return self.inputs.nifti_out



# convert cifti to nifti and back
# Note: this is a quick and dirty implementation. It is not as fexible
# as the wb_command CLI. It's specifically designed to work with scenarios
# where an HCP style cifti needs to be separated. If surfaces or volumes differ
# this could break (e.g. if you have cerebellar surfaces) without additional
# mods
class CiftiSeparateInputSpec(CommandLineInputSpec):
    in_file=File(
        desc="The cifti to ceparate a component of",
        exists=True,
        argstr="%s",
        position=0,
        mandatory=True,
    )

    direction=traits.Enum('COLUMN','ROW', argstr='%s', position=1,
        usedefault=True,
        desc="which direction to separate into components, ROW or COLUMN")


    label=traits.List(Str,
        desc=('list of structures to output. ',
              'CORTEX_LEFT or CORTEX_RIGHT are sensible. ',
              'See wb_command -cifti-separate for more details'),
        argstr='',
        position=2)

    # this needs
    # note that this logic could be adapted for a -volume argument too (for more granular control than volume-all)
    metric=traits.List(Str,
        desc=('list of structures to output. ',
              'CORTEX_LEFT or CORTEX_RIGHT are sensible. ',
              'See wb_command -cifti-separate for more details'),
        argstr='',
        position=3)

    volume_all=traits.Bool(False,
        desc=('separate all volume structures into a volume file. '
              'Populates volume_all_out, roi_all_out and label_all_out output fields'),
        argstr='', # this will be populated automatically by _format_arg()
        position=4,
        usedefault=True)

class CiftiSeparateOutputSpec(TraitedSpec):
    volume_all_out=traits.Either(File(), None)
    volume_all_roi_out=traits.Either(File(), None)
    volume_all_label_out=traits.Either(File(), None)
    CORTEX_LEFT_out=traits.Either(File(), None)
    CORTEX_RIGHT_out=traits.Either(File(), None)


class CiftiSeparate(wb.WBCommand):
    input_spec = CiftiSeparateInputSpec
    output_spec = CiftiSeparateOutputSpec


    _cmd = 'wb_command -cifti-separate'
    metric_files = dict()
    label_files = dict()

    def _format_arg(self, name, spec, value):
        import os

        if name == 'volume_all':
            cwd = os.getcwd()
            fname, _ = os.path.splitext(os.path.basename(self.inputs.in_file))
            fname, _ = os.path.splitext(fname)
            return '-volume-all {0} -roi {1} -label {2}'.format(
                        os.path.join(cwd, fname + '_volume_all.nii.gz'),
                        os.path.join(cwd, fname + '_volume_all_roi.nii.gz'),
                        os.path.join(cwd, fname + '_volume_all_label.nii.gz'))
        if name == 'metric':
            return ' '.join(self._format_metric_arg(v) for v in value)
        if name == 'label':
            return ' '.join(self._format_label_arg(v) for v in value)
        return super(CiftiSeparate, self)._format_arg(name, spec, value)

    def _format_metric_arg(self, structure):
        import os

        fname, _ = os.path.splitext(os.path.basename(self.inputs.in_file))
        fname, _ = os.path.splitext(fname)

        filename = os.path.join(os.getcwd(), fname + '_' + structure + '.func.gii')
        self.metric_files[structure] = filename

        return "-metric {} {}".format(structure, filename)

    
    def _format_label_arg(self, structure):
        import os

        fname, _ = os.path.splitext(os.path.basename(self.inputs.in_file))
        fname, _ = os.path.splitext(fname)

        filename = os.path.join(os.getcwd(), fname + '_' + structure + '.label.gii')
        self.label_files[structure] = filename

        return "-label {} {}".format(structure, filename)

    def _list_outputs(self):
        import os

        outputs = self.output_spec().get()

        if self.inputs.volume_all:
            cwd = os.getcwd();
            fname, _ = os.path.splitext(os.path.basename(self.inputs.in_file))
            fname, _ = os.path.splitext(fname)

            outputs['volume_all_out'] = os.path.join(cwd, fname + '_volume_all.nii.gz')
            outputs['volume_all_roi_out'] = os.path.join(cwd, fname + '_volume_all_roi.nii.gz')
            outputs['volume_all_label_out'] = os.path.join(cwd, fname + '_volume_all_label.nii.gz')
        '''
        if isdefined(self.inputs.metric):
            for structure in self.metric_files:
                outputs[structure + '_out'] = self.metric_files[structure]
        if isdefined(self.inputs.label):
            for structure in self.label_files:
                outputs[structure + '_out'] = self.label_files[structure]

        return outputs
        '''
        if isdefined(self.inputs.metric):
            cwd = os.getcwd()
            fname, _ = os.path.splitext(os.path.basename(self.inputs.in_file))
            fname, _ = os.path.splitext(fname)
            for structure in self.inputs.metric:
                outputs[structure + '_out'] = os.path.join(cwd, f"{fname}_{structure}.func.gii")
        if isdefined(self.inputs.label):
            cwd = os.getcwd()
            fname, _ = os.path.splitext(os.path.basename(self.inputs.in_file))
            fname, _ = os.path.splitext(fname)
            for structure in self.inputs.label:
                outputs[structure + '_out'] = os.path.join(cwd, f"{fname}_{structure}.label.gii")

        return outputs


# Note: this is another quick and dirty implementation. It is not as fexible
# as the wb_command CLI. It's specifically designed to work with scenarios
# where an HCP style cifti needs to be merged. If surfaces or volumes differ
# this could break (e.g. if you have cerebellar surfaces) without additional
# mods
class CiftiCreateDenseTimeseriesInputSpec(CommandLineInputSpec):
    out_file=File(
        argstr='%s',
        position=0,
        genfile=True,
        desc="the output cifti file. Autogenerated if not specified."
    )

    volume=File(
        exists=True,
        desc='volume_file containing all voxel data for all volume structures',
        argstr="-volume %s",
        position=1,
        requires=['volume_label'])

    volume_label=File(
        exists=True,
        desc='label volume file containing labels for cifti structures',
        argstr="%s",
        position=2,
        requires=['volume'])

    left_metric=File(
        exists=True,
        desc="metric for left surface",
        argstr="-left-metric %s",
        position=3)

    left_roi=File(
        exists=True,
        desc="roi of vertices to use from left surface as a metric file",
        argstr="-roi-left %s",
        position=4,
        requires=['left_metric'])

    right_metric=File(
        exists=True,
        desc="metric for the right surface",
        argstr="-right-metric %s",
        position=5)

    right_roi=File(
        exists=True,
        desc="roi of vertices to use from right surface as a metric file",
        argstr="-roi-right %s",
        position=6,
        requires=['right_metric'])

    # cerebellum can be incorporated by copying the left_metric and right_metric implementations
    # note the _format_arg() function though and add appropriate handling there too

class CiftiCreateDenseTimeseriesOutputSpec(TraitedSpec):
    out_file=File(
        exists=True,
        desc="the output cifti file"
    )

class CiftiCreateDenseTimeseries(wb.WBCommand):
    input_spec = CiftiCreateDenseTimeseriesInputSpec
    output_spec = CiftiCreateDenseTimeseriesOutputSpec

    _cmd = 'wb_command -cifti-create-dense-timeseries'


    def _gen_filename(self, name):
        import os

        if name == 'out_file':
            if 'out_file' not in self.inputs.get() or not isdefined(self.inputs.out_file):
                return os.path.join(os.getcwd(), 'dense_cifti.dtseries.nii')
                #self.inputs.out_file = os.path.join(os.getcwd(), 'dense_cifti.dtseries.nii')
            return self.inputs.out_file

    def _list_outputs(self):
        outputs = self.output_spec().get()
        outputs['out_file'] = self._gen_filename('out_file')
        #outputs['out_file'] = self.inputs.out_file

        return outputs




# Note: this is another quick and dirty implementation. It is not as fexible
# as the wb_command CLI. It's specifically designed to work with scenarios
# where an HCP style cifti needs to be merged. If surfaces or volumes differ
# this could break (e.g. if you have cerebellar surfaces) without additional
# mods. Note syntax is basically identical to CiftiCreateDenseTimeseries and
# mods to one should also work on the other.
class CiftiCreateDenseScalarInputSpec(CommandLineInputSpec):
    out_file=File(
        argstr='%s',
        position=0,
        genfile=True,
        desc="the output cifti file. Autogenerated if not specified."
    )

    volume=File(
        exists=True,
        desc='volume_file containing all voxel data for all volume structures',
        argstr="-volume %s",
        position=1,
        requires=['volume_label'])

    volume_label=File(
        exists=True,
        desc='label volume file containing labels for cifti structures',
        argstr="%s",
        position=2,
        requires=['volume'])

    left_metric=File(
        exists=True,
        desc="metric for left surface",
        argstr="-left-metric %s",
        position=3)

    left_roi=File(
        exists=True,
        desc="roi of vertices to use from left surface as a metric file",
        argstr="-roi-left %s",
        position=4,
        requires=['left_metric'])

    right_metric=File(
        exists=True,
        desc="metric for the right surface",
        argstr="-right-metric %s",
        position=5)

    right_roi=File(
        exists=True,
        desc="roi of vertices to use from right surface as a metric file",
        argstr="-roi-right %s",
        position=6,
        requires=['right_metric'])

    # cerebellum can be incorporated by copying the left_metric and right_metric implementations
    # note the _format_arg() function though and add appropriate handling there too

class CiftiCreateDenseScalarOutputSpec(TraitedSpec):
    out_file=File(
        exists=True,
        desc="the output cifti file"
    )

class CiftiCreateDenseScalar(wb.WBCommand):
    input_spec = CiftiCreateDenseScalarInputSpec
    output_spec = CiftiCreateDenseScalarOutputSpec

    _cmd = 'wb_command -cifti-create-dense-scalar'


    def _gen_filename(self, name):
        import os

        if name == 'out_file':
            if 'out_file' not in self.inputs.get() or not isdefined(self.inputs.out_file):
                return os.path.join(os.getcwd(), 'dense_cifti.dscalar.nii')
            return self.inputs.out_file

    def _list_outputs(self):
        outputs = self.output_spec().get()
        outputs['out_file'] = self._gen_filename('out_file')

        return outputs



# Note: this is another quick and dirty implementation. It is not as fexible
# as the wb_command CLI. It's specifically designed to work with scenarios
# where an HCP style cifti needs to be merged. If surfaces or volumes differ
# this could break (e.g. if you have cerebellar surfaces) without additional
# mods. Note syntax is basically identical to CiftiCreateDenseTimeseries and
# mods to one should also work on the other.
class CiftiCreateLabelInputSpec(CommandLineInputSpec):
    out_file=File(
        argstr='%s',
        position=0,
        genfile=True,
        desc="the output cifti file. Autogenerated if not specified."
    )

    volume=File(
        exists=True,
        desc='volume_file containing all voxel data for all volume structures',
        argstr="-volume %s",
        position=1,
        requires=['volume_label'])

    volume_label=File(
        exists=True,
        desc='label volume file containing labels for cifti structures',
        argstr="%s",
        position=2,
        requires=['volume'])

    left_label=File(
        exists=True,
        desc="label for left surface",
        argstr="-left-label %s",
        position=3)

    left_roi=File(
        exists=True,
        desc="roi of vertices to use from left surface as a metric file",
        argstr="-roi-left %s",
        position=4,
        requires=['left_label'])

    right_label=File(
        exists=True,
        desc="label for the right surface",
        argstr="-right-label %s",
        position=5)

    right_roi=File(
        exists=True,
        desc="roi of vertices to use from right surface as a metric file",
        argstr="-roi-right %s",
        position=6,
        requires=['right_label'])

    # cerebellum can be incorporated by copying the left_label and right_label implementations
    # note the _format_arg() function though and add appropriate handling there too

class CiftiCreateLabelOutputSpec(TraitedSpec):
    out_file=File(
        exists=True,
        desc="the output cifti file"
    )

class CiftiCreateLabel(wb.WBCommand):
    input_spec = CiftiCreateLabelInputSpec
    output_spec = CiftiCreateLabelOutputSpec

    _cmd = 'wb_command -cifti-create-label'


    def _gen_filename(self, name):
        import os

        if name == 'out_file':
            if 'out_file' not in self.inputs.get() or not isdefined(self.inputs.out_file):
                return os.path.join(os.getcwd(), 'dense_cifti.dlabel.nii')
            return self.inputs.out_file

    def _list_outputs(self):
        outputs = self.output_spec().get()
        outputs['out_file'] = self._gen_filename('out_file')

        return outputs


# another quick and dirty implementation
class CiftiMergeInputSpec(CommandLineInputSpec):
    out_file=File(
        argstr='%s',
        position=0,
        genfile=True,
        desc="The output cifti file. Autogenerated if not specified."
    )

    cifti=traits.List(File(exists=True),
        desc='specify an input cifti file list',
        argstr='-cifti %s...',
        mandatory=True,
        position=1)

class CiftiMergeOutputSpec(TraitedSpec):
    out_file=File(
        exists=True,
        desc="the output cifti file"
    )

class CiftiMerge(wb.WBCommand):
    input_spec = CiftiMergeInputSpec
    output_spec = CiftiMergeOutputSpec

    _cmd = 'wb_command -cifti-merge'

    def _gen_filename(self, name):
        import os

        if name == 'out_file':
            if 'out_file' not in self.inputs.get() or not isdefined(self.inputs.out_file):
                return os.path.join(os.getcwd(), 'merged_cifti.dscalar.nii')
            return self.inputs.out_file

    def _list_outputs(self):
        outputs = self.output_spec().get()
        if 'out_file' not in outputs or not isdefined(outputs['out_file']):
            outputs['out_file'] = self._gen_filename('out_file')

        return outputs


# Drafted by chatGPT
class ParcellateInputSpec(CommandLineInputSpec):
    in_file = File(
        exists=True,
        argstr="%s",
        position=0,
        mandatory=True,
        desc="Input CIFTI data file (e.g., dtseries.nii or dscalar.nii)"
    )

    parcellation = File(
        exists=True,
        argstr="%s",
        position=1,
        mandatory=True,
        desc="CIFTI label file defining parcels (e.g., a dlabel.nii)"
    )

    direction = traits.Enum(
        "COLUMN",
        argstr="%s",
        position=2,
        usedefault=True,
        desc="Reduction direction (only COLUMN is valid)"
    )

    out_file = File(
        argstr="%s",
        position=3,
        genfile=True,
        desc="Output CIFTI file"
    )

    method = traits.Enum(
        "MEAN", "MODE", "MEDIAN", "SUM", "STDEV", "VARIANCE",
        argstr="-method %s",
        position=4,
        desc="Statistical method to apply for parcellation"
    )


class ParcellateOutputSpec(TraitedSpec):
    out_file = File(
        exists=True,
        desc="Parcellated output CIFTI file"
    )


class Parcellate(wb.WBCommand):
    input_spec = ParcellateInputSpec
    output_spec = ParcellateOutputSpec

    _cmd = 'wb_command -cifti-parcellate'

    def _gen_filename(self, name):
        import os
        if name == 'out_file':
            if not isdefined(self.inputs.out_file):
                base, _ = os.path.splitext(os.path.basename(self.inputs.in_file))
                base, _ = os.path.splitext(base)
                return os.path.join(os.getcwd(), base + '_parcellated.ptseries.nii')
            return self.inputs.out_file

    def _list_outputs(self):
        outputs = self.output_spec().get()
        outputs['out_file'] = self._gen_filename('out_file')
        return outputs


# CiftiReduce interfaces drafted by chatGPT
class ReduceInputSpec(CommandLineInputSpec):
    in_file = File(
        exists=True,
        argstr="%s",
        position=0,
        mandatory=True,
        desc="Input CIFTI file"
    )

    direction = traits.Enum("ROW", "COLUMN",
        argstr="%s",
        position=1,
        usedefault=True,
        desc="Direction to reduce along")

    operation = traits.Enum(
        "MEAN", "MEDIAN", "MAX", "MIN", "STDEV", "VARIANCE",
        "SUM", "PRODUCT", "INDEXMAX", "INDEXMIN", "MODE",
        "COUNT_NONZERO", "L2NORM", "TSNR",
        argstr="-reduce %s",
        position=2,
        mandatory=True,
        desc="Reduction operation to apply")

    exclude_outliers = traits.Tuple(
        (traits.Float, traits.Float),
        argstr="-exclude-outliers %f %f",
        desc="Trim values beyond σ‑below and σ‑above")

    only_numeric = traits.Bool(
        argstr="-only-numeric",
        desc="Filter non‑numeric values before reduction")

    out_file = File(
        argstr="%s",
        position=-1,
        genfile=True,
        desc="Output CIFTI file name")

class ReduceOutputSpec(TraitedSpec):
    out_file = File(
        exists=True,
        desc="Reduced output CIFTI file"
    )

class Reduce(wb.WBCommand):
    input_spec = ReduceInputSpec
    output_spec = ReduceOutputSpec

    _cmd = 'wb_command -cifti-reduce'

    def _gen_filename(self, name):
        import os
        if name == 'out_file':
            if not isdefined(self.inputs.out_file):
                base, ext = os.path.splitext(os.path.basename(self.inputs.in_file))
                base = os.path.splitext(base)[0]
                return os.path.join(os.getcwd(), f"{base}_reduced.dscalar.nii")
            return self.inputs.out_file

    def _list_outputs(self):
        outputs = self.output_spec().get()
        outputs["out_file"] = self._gen_filename("out_file")
        return outputs


# partial implementation
# TODO: 
# - add support for cropped input
# - add support for label inputs
# - add support for volume inputs (other than -volume-all)
class CiftiCreateDenseFromTemplateInputSpec(CommandLineInputSpec):
    template=File(
        argstr='%s',
        position=0,
        exists=True,
        mandatory=True,
        desc="file to match brainordinates of")

    out_file=File(
        argstr='%s',
        position=1,
        desc="the output cifti file. Autogenerated if not specified.",
        genfile=True,
    )
    
    series=traits.BaseTuple((traits.Float(), traits.Float()),
        position=2,
        argstr='-series %s %s',
        desc="make a dtseries file instead of a dscalar. Takes (<step>, <start>) as input. \
              step is increment between points. start is initial step value at first volume.")
    
    series_unit=traits.Enum(_valid_cifti_units,
        position=3,
        argstr='-unit %s',
        desc="unit identifier for series (default SECOND)")

    volume_all=File(
        exists=True,
        desc='Specify an input volume file for all voxel data',
        argstr="-volume-all %s",
        position=-1)

    metric=List(traits.BaseTuple(traits.Enum(_valid_cifti_structs), File),
        exists=True,
        argstr="-metric %s %s...",
        position=-2,
        desc=f"List of tuples (struct, file_path) where structure is a string from {_valid_cifti_structs}")
        
    cifti=List(File,
        exists=True,
        position=-3,
        argstr='-cifti %s...',
        desc="repeatable - use input data from cifti file")
        
    label_collision=traits.Enum('ERROR', 'SURFACES_FIRST', 'LEGACY',
        position=-4,
        argstr='-label-collision %s',
        desc="How to handle conflicts between label keys. Legacy matches wb_command v.1.4.2 \
              and earlier. (default ERROR)")

    # cerebellum can be incorporated by copying the left_metric and right_metric implementations
    # note the _format_arg() function though and add appropriate handling there too

class CiftiCreateDenseFromTemplateOutputSpec(TraitedSpec):
    out_file=File(
        exists=True,
        desc="the output cifti file"
    )

class CiftiCreateDenseFromTemplate(wb.WBCommand):
    input_spec = CiftiCreateDenseFromTemplateInputSpec
    output_spec = CiftiCreateDenseFromTemplateOutputSpec

    _cmd = 'wb_command -cifti-create-dense-from-template'

    def _gen_filename(self, name):
        import os

        if name == 'out_file':
            if 'out_file' not in self.inputs.get() or not isdefined(self.inputs.out_file):
                basename = os.path.basename(self.inputs.template)
                
                # force dtseries.nii extension if a timeseries format
                if self.inputs.series:
                    return os.path.join(os.getcwd(), 'dense_cifti.dtseries.nii')

                # use template extension
                ext = ''
                base, this_ext = os.path.splitext(basename)
                while this_ext:
                    ext = this_ext + ext
                    base, this_ext = os.path.splitext(base)
                    
                return os.path.join(os.getcwd(), 'dense_cifti' + ext)
            else:
                basename = os.path.basename(self.inputs.out_file)
                return os.path.join(os.getcwd(), basename)

    def _list_outputs(self):
        outputs = self.output_spec().get()
        outputs['out_file'] = self._gen_filename('out_file')

        return outputs
    


# another quick and dirty implementation
class CiftiMergeInputSpec(CommandLineInputSpec):
    out_file=File(
        argstr='%s',
        position=0,
        genfile=True,
        desc="The output cifti file. Autogenerated if not specified."
    )

    cifti=traits.List(File(exists=True),
        desc='specify an input cifti file list',
        argstr='-cifti %s...',
        mandatory=True,
        position=1)

class CiftiMergeOutputSpec(TraitedSpec):
    out_file=File(
        exists=True,
        desc="the output cifti file"
    )

class CiftiMerge(wb.WBCommand):
    input_spec = CiftiMergeInputSpec
    output_spec = CiftiMergeOutputSpec

    _cmd = 'wb_command -cifti-merge'

    def _gen_filename(self, name):
        import os

        if name == 'out_file':
            if 'out_file' not in self.inputs.get() or not isdefined(self.inputs.out_file):
                return os.path.join(os.getcwd(), 'merged_cifti.dscalar.nii')
            return self.inputs.out_file

    def _list_outputs(self):
        outputs = self.output_spec().get()
        if 'out_file' not in outputs or not isdefined(outputs['out_file']):
            outputs['out_file'] = self._gen_filename('out_file')

        return outputs

# This has not yet been tested with the roi option, which changes the output format
# from a float or list of floats to a list of list of floats.
class CiftiStatsInputSpec(CommandLineInputSpec):
    in_file=Str(
        argstr='%s',
        position=0,
        desc="the input cifti"
    )
    
    reduce=traits.Enum('MAX','MIN','INDEXMAX','INDEXMIN','SUM','PRODUCT','MEAN',
        'STDEV','SAMPSTDEV','VARIANCE','TSNR','COV','L2NORM','MEDIAN','MODE','COUNT_NONZERO',
        argstr='-reduce %s', 
        position=1,
        mandatory=False,
        desc="use a reduction operation",
        xor=['percentile'])
        
    percentile=traits.Float(
        argstr='-percentile %s',
        position=1,
        mandatory=False,
        desc="give the value at a percentile",
        xor=['reduce'])

    column=traits.Int(
        argstr='-column %s', 
        position=2,
        desc="only display output for one column")

    roi=File(
        argstr='-roi %s',
        position=3,
        desc="only consider data inside an roi")
        
    match_maps=traits.Bool(False,
        argstr='-match-maps',
        position=4,
        desc="each column of input uses the corresponding column from the roi file",
        requires=['roi'])
        
    show_map_name=traits.Bool(False,
        argstr='-show-map-name',
        desc="print column index and name before each output")

class CiftiStatsOutputSpec(TraitedSpec):
    value=traits.Either(traits.Float(), 
                        traits.List(traits.Float()), 
                        traits.List(traits.List(traits.Float())),
        desc="For each column of the input a list element is returned resulting from the specified reduction or percentile operation"
    )

class CiftiStats(wb.WBCommand):
    input_spec = CiftiStatsInputSpec
    output_spec = CiftiStatsOutputSpec

    _cmd = 'wb_command -cifti-stats'

    # function below drafted by chatGPT
    def aggregate_outputs(self, runtime=None, needed_outputs=None):
        outputs = self._outputs()
        
        # Capture and process the output from the command-line execution
        if runtime is None:
            runtime = self.run()
        
        # Parse the output
        try:
            output_values = [float(x) for x in runtime.stdout.strip().split()]
            # Assign the parsed values to the output trait
            if len(output_values) == 1:
                outputs.value = output_values[0]  # Single float value
            else:
                outputs.value = output_values  # List of values
        except ValueError:
            outputs.value = None
        
        return outputs




class CiftiSmoothingInputSpec(CommandLineInputSpec):
    in_file=File(
        exists=True,
        argstr='%s',
        position=0,
        desc="the input cifti file.")

    surface_kernel=traits.Float(
        argstr='%s',
        mandatory=True,
        position=1,
        desc="the size of the gaussian surface smoothing kernel in mm, as sigma by default")

    volume_kernel=traits.Float(
        argstr='%s',
        mandatory=True,
        position=2,
        desc="the size of the gaussian volume smoothing kernel in mm, as sigma by default")
        
    direction=traits.Enum('COLUMN','ROW', 
        argstr='%s',
        usedefault=True,
        position=3,
        desc="which dimension to smooth along, ROW or COLUMN")       
        
    out_file=File(
        argstr='%s',
        position=4,
        genfile=True,
        desc="the output cifti file. Autogenerated if not specified.")
    
    fwhm=traits.Bool(
        argstr='-fwhm',
        mandatory=False,
        position=5,
        desc="kernel sizes are fwhm not sigma")

    left_surface=File(
        argstr='-left-surface %s',
        exists=True,
        desc='specify the left surface to use',
        position=6)
        
    left_corrected_areas=File(
        requires=['left_surface'],
        argstr='-left-corrected-areas %s',
        exists=True,
        desc="vertex areas to use instead of computing them from the left surface, as a metric",
        position=7)

    right_surface=File(
        argstr='-right-surface %s',
        exists=True,
        desc='specify the right surface to use',
        position=8)
        
    right_corrected_areas=File(
        requires=['right_surface'],
        argstr='-right-corrected-areas %s',
        exists=True,
        desc="vertex areas to use instead of computing them from the right surface, as a metric",
        position=9)

    cerebellum_surface=File(
        argstr='-cerebellum-surface %s',
        exists=True,
        desc='specify the cerebellum surface to use',
        position=10)
        
    cerebellum_corrected_areas=File(
        requires=['cerebellum_surface'],
        argstr='-cerebellum-corrected-areas %s',
        exists=True,
        desc="vertex areas to use instead of computing them from the cerebellum surface, as a metric",
        position=11)

    cifti_roi=File(
        exists=True,
        desc="smooth only within regions of interest",
        argstr="-cifti-roi %s",
        position=12)

    fix_zeros_volume=traits.Bool(
        argstr='-fix-zeros-volume',
        mandatory=False,
        position=13,
        desc="treat values of zero in the volume as missing data")
        
    fix_zeros_surface=traits.Bool(
        argstr='-fix-zeros-surface',
        mandatory=False,
        position=14,
        desc="treat values of zero on the surface as missing")
        
    merged_volume=traits.Bool(
        argstr='-merged-volume',
        mandatory=False,
        position=15,
        desc="smooth across subcortical structure boundaries")

class CiftiSmoothingOutputSpec(TraitedSpec):
    out_file=File(
        exists=True,
        desc="the output cifti file"
    )

class CiftiSmoothing(wb.WBCommand):
    input_spec = CiftiSmoothingInputSpec
    output_spec = CiftiSmoothingOutputSpec

    _cmd = 'wb_command -cifti-smoothing'


    def _gen_filename(self, name):
        import os

        if name == 'out_file':
            if 'out_file' not in self.inputs.get() or not isdefined(self.inputs.out_file):
                basename = os.path.basename(self.inputs.in_file)

                ext = ''
                base, this_ext = os.path.splitext(basename)
                while this_ext:
                    ext = this_ext + ext
                    base, this_ext = os.path.splitext(base)
                    
                return os.path.join(os.getcwd(), base + '_smoothed' + ext)
            return self.inputs.out_file

    def _list_outputs(self):
        outputs = self.output_spec().get()
        outputs['out_file'] = self._gen_filename('out_file')

        return outputs



# Note: this is another quick and dirty implementation. The dirt comes down to
# specifications of suboptions to -var, which can take -select x y -repeat type
# option. If you want to pass something like that implement a Function interface
# that takes your input file name as input and returns a string that includes
# that filename and the subsequent modifiers.
class CiftiMathInputSpec(CommandLineInputSpec):
    expression=Str(
        argstr='"%s"',
        position=0,
        desc="a mathematical expression to evaluate"
    )
    out_file=File(
        argstr='%s',
        position=1,
        genfile=True,
        desc="the output cifti file. Autogenerated if not specified."
    )
    in_vars=traits.List(
        traits.Tuple(Str(),
                     traits.Either(File(exists=True),
                                   Str())),
        desc='repeatable - a cifti file to use as a variable',
        argstr='-var "%s" %s...',
        mandatory=True,
        position=2
    )

class CiftiMathOutputSpec(TraitedSpec):
    out_file=File(
        exists=True,
        desc="the output cifti file"
    )

class CiftiMath(wb.WBCommand):
    input_spec = CiftiMathInputSpec
    output_spec = CiftiMathOutputSpec

    _cmd = 'wb_command -cifti-math'


    def _gen_filename(self, name):
        import os

        if name == 'out_file':
            if 'out_file' not in self.inputs.get() or not isdefined(self.inputs.out_file):
                return os.path.join(os.getcwd(), 'cifti_math_results.dscalar.nii')
            return self.inputs.out_file

    def _list_outputs(self):
        outputs = self.output_spec().get()
        outputs['out_file'] = self._gen_filename('out_file')

        return outputs



# incomplete: does not support weighted averaging
class AverageInputSpec(CommandLineInputSpec):
    out_file=File(
        argstr='%s',
        position=0,
        genfile=True,
        desc="the output cifti file. Autogenerated if not specified."
    )

    exclude_outliers=List(traits.Tuple(traits.Float(), traits.Float()),
        position=1,
        argstr='-exclude-outliers %f %f',
        mandatory=False,
        desc="Exclude outliers by standard deviaiton of each element across files. Takes List of standard deviations above and below:(sigma-below, sigma-above)"
    )

    in_vars=traits.List(File(exists=True),
        desc='repeatable - specify input ciftis',
        argstr='-cifti %s...',
        mandatory=True,
        position=2
    )

class AverageOutputSpec(TraitedSpec):
    out_file=File(
        exists=True,
        desc="the output cifti file"
    )

class Average(wb.WBCommand):
    input_spec = AverageInputSpec
    output_spec = AverageOutputSpec

    _cmd = 'wb_command -cifti-average'


    def _gen_filename(self, name):
        import os

        if name == 'out_file':
            if 'out_file' not in self.inputs.get() or not isdefined(self.inputs.out_file):
                return os.path.join(os.getcwd(), 'cifti_average.dscalar.nii')
            return self.inputs.out_file

    def _list_outputs(self):
        outputs = self.output_spec().get()
        outputs['out_file'] = self._gen_filename('out_file')

        return outputs