<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const props = defineProps({ id: String })
const run = ref(null)
onMounted(async () => { run.value = await getJSON(`/api/runs/${props.id}`) })
</script>
<template>
  <div class="page" v-if="run"><h1>记录 #{{ run.id }}</h1>
  <p>{{ run.wall_name }} → {{ run.roll_name }}</p>
  <p><strong>{{ run.result.rolls }} 卷</strong> · {{ run.result.drops }} 条 · 每条 {{ run.result.drop_len_m }}m · 每卷 {{ run.result.strips_per_roll }} 条</p>
  <p v-if="run.note">备注：{{ run.note }}</p>
  <p>{{ run.created_at }}</p></div>
</template>
