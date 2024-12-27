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

'''
LabelResample interface using nipype.interfaces.workbench.metric.py
as a starting point.
'''

class LabelResampleInputSpec(CommandLineInputSpec):
    in_file = File(
        exists=True,
        mandatory=True,
        argstr="%s",
        position=0,
        desc="The label file to resample",
    )
    current_sphere = File(
        exists=True,
        mandatory=True,
        argstr="%s",
        position=1,
        desc="A sphere surface with the mesh that the label is currently on",
    )
    new_sphere = File(
        exists=True,
        mandatory=True,
        argstr="%s",
        position=2,
        desc="A sphere surface that is in register with <current-sphere> and"
        " has the desired output mesh",
    )
    method = traits.Enum(
        "ADAP_BARY_AREA",
        "BARYCENTRIC",
        argstr="%s",
        mandatory=True,
        position=3,
        desc="The method name - ADAP_BARY_AREA method is recommended for"
        " ordinary metric data, because it should use all data while"
        " downsampling, unlike BARYCENTRIC. If ADAP_BARY_AREA is used,"
        " exactly one of area_surfs or area_metrics must be specified",
    )
    out_file = File(
        name_source=["new_sphere"],
        name_template="%s.nii",
        keep_extension=True,
        argstr="%s",
        position=4,
        desc="The output label",
    )
    area_surfs = traits.Bool(
        position=5,
        argstr="-area-surfs",
        xor=["area_metrics"],
        desc="Specify surfaces to do vertex area correction based on",
    )
    area_metrics = traits.Bool(
        position=5,
        argstr="-area-metrics",
        xor=["area_surfs"],
        desc="Specify vertex area metrics to do area correction based on",
    )
    current_area = File(
        exists=True,
        position=6,
        argstr="%s",
        desc="A relevant anatomical surface with <current-sphere> mesh",
    )
    new_area = File(
        exists=True,
        position=7,
        argstr="%s",
        desc="A relevant anatomical surface with <current-sphere> mesh",
    )
    roi_metric = File(
        exists=True,
        position=8,
        argstr="-current-roi %s",
        desc="Input roi on the current mesh used to exclude non-data vertices",
    )
    valid_roi_out = traits.Bool(
        position=9,
        argstr="-valid-roi-out",
        desc="Output the ROI of vertices that got data from valid source vertices",
    )
    largest = traits.Bool(
        position=10,
        argstr="-largest",
        desc="Use only the value of the vertex with the largest weight",
    )


class LabelResampleOutputSpec(TraitedSpec):
    out_file = File(exists=True, desc="the output label")
    roi_file = File(desc="ROI of vertices that got data from valid source vertices")


class LabelResample(wb.WBCommand):
    """
    Resample a label file to a different mesh

    Resamples a label file, given two spherical surfaces that are in
    register.  If ``ADAP_BARY_AREA`` is used, exactly one of -area-surfs or
    ``-area-metrics`` must be specified.

    The ``ADAP_BARY_AREA`` method is recommended for ordinary label data,
    because it should be better at resolving vertices that are near multiple 
    labels, or in case of downsampling.  Midthickness surfaces are recommended 
    for the vertex areas for most data.

    The ``-largest option`` results in nearest vertex behavior when used with
    ``BARYCENTRIC``, as it uses the value of the source vertex that has the 
    largest weight.

    When ```-largest``` is not specified, the vertex weights are summed according
    to which label they correspond to, and the label with the largest sum is 
    used.
    """

    input_spec = LabelResampleInputSpec
    output_spec = LabelResampleOutputSpec
    _cmd = "wb_command -label-resample"

    def _format_arg(self, opt, spec, val):
        if opt in ["current_area", "new_area"]:
            if not self.inputs.area_surfs and not self.inputs.area_metrics:
                raise ValueError(
                    "{} was set but neither area_surfs or"
                    " area_metrics were set".format(opt)
                )
        if opt == "method":
            if (
                val == "ADAP_BARY_AREA"
                and not self.inputs.area_surfs
                and not self.inputs.area_metrics
            ):
                raise ValueError(
                    "Exactly one of area_surfs or area_metrics must be specified"
                )
        if opt == "valid_roi_out" and val:
            # generate a filename and add it to argstr
            roi_out = self._gen_filename(self.inputs.in_file, suffix="_roi")
            iflogger.info("Setting roi output file as", roi_out)
            spec.argstr += " " + roi_out
        return super()._format_arg(opt, spec, val)

    def _list_outputs(self):
        outputs = super()._list_outputs()
        if self.inputs.valid_roi_out:
            roi_file = self._gen_filename(self.inputs.in_file, suffix="_roi")
            outputs["roi_file"] = os.path.abspath(roi_file)
        return outputs