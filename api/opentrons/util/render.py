
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


def render_well(well, liquid_tracker):
    # Offset child coordinates by parent, and scale from mm to pixels
    # parent = well.get_parent()
    # x, y, z = (well.coordinates() - parent.coordinates()) * SCALE
    x, y, z = well.coordinates() * SCALE
    # TODO: pie chart / bar graph of %s
    liquids = liquid_tracker[well].liquids
    # HACK: for now, just using the liquid w highest volume in the well
    fill_color = sorted(liquids.keys() or ['white'])[-1]

    if 'diameter' in well.properties:
        # It's a circular well
        return '<circle cx="{cx}" cy="{cy}" r="{radius}" fill={fill} \
            class="{class_name}" data-well-name="{well_name}"/>'.format(
                cx=x,
                cy=y,
                radius=well.properties['diameter'] / 2 * SCALE,
                well_name=well.get_name(),
                class_name='ot-well',
                fill=fill_color
            )
    elif 'width' in well.properties and 'length' in well.properties:
        return '<rect x="{x}" y="{y}" width="{width}" height="{length}" \
            fill="{fill}" class="{class_name}" data-well-name="{well_name}"/>'.format(  # noqa: E501
                x=x,
                y=y,
                length=well.properties['length'] * SCALE,
                width=well.properties['width'] * SCALE,
                well_name=well.get_name(),
                class_name='ot-well',
                fill=fill_color
        )
    else:
        # TODO: remove/rewrite -- this is for my debugging
        # TODO: should this be some visual red 'X'?
        # Or stop rendering completely?
        print(
            'warning: well has no diameter, ' +
            'and has no width and/or length', well)


def render_container(container, liquid_tracker):
    return (
        well_style +
        # transform to flip y axis.
        # Robot origin is bottom left, SVG is top left.
        #
        # TODO: don't inline height
        '<svg style="height: 20em; width: 100%;" transform="scale(1, -1)">' +
        ''.join([
            render_well(well, liquid_tracker)
            for well in container.wells()
        ]) +
        '</svg>')


def render_deck_svg(robot):
    return (
        well_style +
        '<svg style="height: 36em; width: 100%;" transform="scale(1, -1)">' +
        ''.join([
            render_well(well, robot.liquid_tracker)
            for container in robot.get_containers()
            for well in container.wells()
        ]) +
        '</svg>')
