import { createWebHistory, createRouter } from 'vue-router'

import ApartmentView from './components/ApartmentView.vue'
import ApartmentListView from './components/ApartmentListView.vue'
import CompareApartmentView from './components/CompareApartmentView.vue'
import StatisticView from './components/StatisticView.vue'
import HomeView from './components/HomeView.vue'

const routes = [
    { path: '/', component: HomeView },
    { path: '/apartments', component: ApartmentListView },
    { path: '/apartments/:apartmentId', component: ApartmentView },
    { path: '/compare', component: CompareApartmentView },
    { path: '/statistic', component: StatisticView },
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

export default router