import opentrons.containers as containers

# Fixed dimensions in millimeters
SLOT_HEIGHT = 127.76
SLOT_WIDTH = 85.47
SLOT_SPACER = 5.0

DECK_HEIGHT = (SLOT_HEIGHT * 3 + SLOT_SPACER * 2)
DECK_WIDTH = (SLOT_WIDTH * 5 + SLOT_SPACER * 4)

TOP_MARGIN = 10  # millimeters, is converted to px

well_style = """
<style>
.ot-liquid-deckmap {
    width: 80%;
}

.ot-well-detail-view, .ot-container-detail {
    width: 80%;
}


.ot-well {
    position: relative;
    stroke: black;
}

.ot-well-label {
    fill: transparent;
}

/*
    .ot-well-label:hover {
        visibility: visible;
        fill: blue;
        }
*/

.ot-slot-outline {
    fill: none;
    stroke: orange;
}
</style>
"""


def render_well(well, liquid_tracker, offset=None, svg_height=None):
    x, y, z = well.coordinates() - (offset or (0, 0, 0))
    if svg_height is not None:
        # invert the y axis, robot is bottom left while svg is top left.
        y = svg_height - y

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
                radius=well.properties['diameter'] / 2,
                well_name=well.get_name(),
                class_name='ot-well',
                fill=fill_color
            )
    elif 'width' in well.properties and 'length' in well.properties:
        # rectangular well
        return '<rect x="{x}" y="{y}" width="{width}" height="{length}" \
            fill="{fill}" class="{class_name}" data-well-name="{well_name}"/>'.format(  # noqa: E501
                x=x,
                y=y,
                length=well.properties['length'],
                width=well.properties['width'],
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


def render_container_detail(container, liquid_tracker):
    offset = container[0].coordinates()
    #  + container.get_parent().coordinates()
    return (
        well_style +
        # TODO IMMEDIATELY: test this again, or trash it
        '<svg class="ot-container-detail">' +
        ''.join([
            render_well(well, liquid_tracker, offset, svg_height=SLOT_HEIGHT)
            for well in container.wells()
        ]) +
        '</svg>')


def render_deck(robot):
    def render_slot(slot):
        # TODO: containers don't match up with slots! Ugly.
        slot_offset = robot.deck['A1'].coordinates()
        x, y, z = slot.coordinates() + slot_offset
        # y = flip_y(y)
        return '<rect x="{x}" y="{y}" width="{width}" height="{height}" \
            class="ot-slot-outline" />'.format(
                x=x,
                y=y,
                height=SLOT_HEIGHT,
                width=SLOT_WIDTH)

    return (
        ''.join([
            well_style,
            '<svg class="ot-liquid-deckmap" \
            viewbox="0 0 {width} {height}">'.format(
                width=DECK_WIDTH,
                height=DECK_HEIGHT),
            '<g>',
            ''.join([
                render_well(
                    well,
                    robot.liquid_tracker,
                    svg_height=DECK_HEIGHT)
                for container in robot.get_containers()
                for well in container.wells()
            ]),
            # ''.join([
            #     render_slot(slot) for slot in robot.deck.get_children_list()
            # ]),
            '</g>',
            '</svg>'
        ])
    )


class Display():
    # This class is used for rendering containers and instruments on the robot.
    # liquid tracking data is tied to a robot instance,
    # so Display needs a robot to reference.
    def __init__(self, entity, robot):
        self.entity = entity
        self.robot = robot

    def _repr_html_(self):
        # _repr_html_ is jupyter notebook magic to display html
        if type(self.entity) is containers.Deck:
            return render_deck(self.robot)

        if type(self.entity) is containers.Well:
            # TODO: (Ian 2017-09-07) make a separate
            # render fn for individual well view, this is ugly.
            well = self.entity
            return (
                '<svg class="ot-well-detail" viewbox="0 0 200 100">' +
                render_well(
                    well,
                    self.robot.liquid_tracker,
                    # TODO: offset circular wells by radius on x
                    offset=well.coordinates(),
                    svg_height=(
                        well.properties.get('length', None) or
                        well.properties.get('diameter', 0))
                ) + '</svg>'
            )

        if type(self.entity) is containers.Container:
            return render_container_detail(
                self.entity,
                self.robot.liquid_tracker
            )

        # fallback to __repr__
        return repr(self.entity)
