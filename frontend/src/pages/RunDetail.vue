<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
import DropStripBar from '../components/DropStripBar.vue'
const props = defineProps({ id: String })
const run = ref(null)
onMounted(async () => { run.value = await getJSON(`/api/runs/${props.id}`) })
</script>
<template>
  <div class="page"><h1>记录详情</h1>
    <div v-if="run">
      <p>{{ run.wall_name }} × {{ run.roll_name }}</p>
      <strong>{{ run.result.rolls }} 卷</strong> · {{ run.result.drops }} 条 · 每条 {{ run.result.drop_len_m }}m
      <p>每卷 {{ run.result.strips_per_roll }} 条 · 对花 {{ run.result.pattern_m }}m</p>
      <DropStripBar :drops="run.result.drops" :drop-len="run.result.drop_len_m" :rolls="run.result.rolls" />
      <p>{{ run.created_at }} {{ run.note }}</p>
    </div>
  </div>
</template>
