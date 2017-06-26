<template>
  <div class='placeable' @click='jogToSlot()'>
    <router-link :to="link()">
    <span v-if="wells">
      <svg v-if="!drawRect" :width="width" :viewBox="viewBox" width='100%' preserveAspectRatio='xMinYMin meet'>
        <g>
          <circle v-for="(well, key) in wells"  fill='blue' stroke='white' :cx='well.x' :cy='slotDimY-well.y' :r='well.diameter/2' :class="['well', key]">
          </circle>
        </g>
      </svg>
      <svg v-else viewBox='0 0 85.5 127.75' width='100%' preserveAspectRatio='xMinYMin'>
        <g>
          <rect v-for="(well, key) in wells"  fill='blue' stroke='white' :x='well.x - well.width/2' :y='slotDimY-well.y - well.length/2' :width='well.width' :height="well.length" :class="['trough', key]"></rect>
        </g>
      </svg>
    </span>
    </router-link>
  </div>
</template>

<script>
export default {
  name: 'Container',
  props: ['placeable'],
  data () {
    return {
      show: false,
      container: null,
      slotDimX: 85.5,
      slotDimY: 127.75,
      drawRect: false,
      scaler: 1,
      width: 50
    }
  },
  computed: {
    wells () {
      this.container = this.$store.state.apiContainers[this.placeable.type]
      let wells = this.container['locations']
      if (wells['A1']['length']) { this.drawRect = true }
      return wells
    },
    containersPerSlot () {
      let deck = this.$store.state.tasks.deck
      let sameSlot = deck.filter((placeable) => {
        return placeable.slot === this.placeable.slot
      })
      return sameSlot.length
    },
    viewBox () {
      return '0 0 85.5 ' + 127.75 / this.containersPerSlot
    }
  },
  methods: {
    jogToSlot (slot) {
      if (!this.$store.state.busy) {
        this.$store.dispatch('jogToSlot', {slot: this.placeable.slot})
      }
    },
    normalize (value) {
      return value * this.scaler
    },
    link () {
      let axis = this.$route.params.instrument
      return this.placeable.href[axis] || this.$route.path
    }
  },
  mounted () {
    this.width = this.$el.clientWidth
    this.scaler = this.$el.clientWidth / this.slotDimX
  }
}
</script>