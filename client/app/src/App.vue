<script setup>
// import { ref } from 'vue'
// import ApartmentListView from './components/ApartmentListView.vue'
// import StatisticView from './components/StatisticView.vue'

// const toggle = ref("lists")

// const changePage = () => {
//   if (toggle.value === "lists") {
//     toggle.value = "statistic"
//   } else if (toggle.value === "statistic") {
//     toggle.value = "lists"
//   }
// }
</script>

<template>
  <nav class="navbar navbar-light bg-light">
    <div class="container-fluid justify-content-start">
      <RouterLink class="btn btn-sm" to="/">головна сторінка</RouterLink>
      <RouterLink class="btn btn-sm" to="/apartments?skip=0&limit=20">нерухомость</RouterLink>
      <RouterLink class="btn btn-sm" to="/compare">порівняти ціни</RouterLink>
      <RouterLink class="btn btn-sm" to="/statistic">статистика</RouterLink>
    </div>
  </nav>
  <main>
    <RouterView :key="$route.fullPath" />
  </main>
</template>
