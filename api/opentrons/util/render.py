SCALE = 2  # used to scale millimeters to pixels


well_style = """
<style>
.ot-well {
    position: relative;
    stroke: black;
}

.ot-well-label {
    fill: transparent;
}

.ot-well-label:hover {
    visibility: visible;
    fill: blue;
}
</style>
"""


def render_well(well):
    parent = well.get_parent()
    # Offset child coordinates by parent, and scale from mm to pixels
    x, y, z = (well.coordinates() - parent.coordinates()) * SCALE

    if 'diameter' in well.properties:
        # It's a circular well
        return '<circle cx="{cx}" cy="{cy}" r="{radius}" fill={fill} class="{class_name}" data-well-name="{well_name}"/>'.format(  # noqa: E501
                cx=x,
                cy=y,
                radius=well.properties['diameter'] / 2 * SCALE,
                well_name=well.get_name(),
                class_name='ot-well',
                fill='red'  # TODO: use liquid tracking to set fill color
            )
    elif 'width' in well.properties and 'length' in well.properties:
        return '<rect x="{x}" y="{y}" width="{width}" height="{length}" fill="{fill}" class="{class_name}" data-well-name="{well_name}"/>'.format(  # noqa: E501
            x=x,
            y=y,
            length=well.properties['length'] * SCALE,
            width=well.properties['width'] * SCALE,
            well_name=well.get_name(),
            class_name='ot-well',
            fill='blue'  # TODO: use liquid tracking to set fill color
        )
    else:
        #  TODO: remove/rewrite -- this is for my debugging
        print(
            'warning: well has no diameter, ' +
            'and has no width and/or length', well)


def render_container(container):
    return (
        well_style +
        # transform to flip y axis.
        # Robot origin is bottom left, SVG is top left.
        #
        # TODO: don't inline height
        '<svg style="height: 20em;" transform="scale(1, -1)">' +
        ''.join([render_well(well) for well in container.wells()]) +
        '</svg>')
