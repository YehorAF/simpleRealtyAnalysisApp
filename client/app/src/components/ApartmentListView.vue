<script setup>
import { ref, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const dataset = ref([])
const limit = ref(Number.parseInt(route.query.limit) || 20)
const skip = ref(Number.parseInt(route.query.skip) || 0)
const max = ref(0)
const lastSkip = ref(0)

const town = ref("")
const towns = ref([])

if (Array.isArray(route.query.towns)) {
    towns.value = route.query.towns
} else if (route.query.towns && route.query.towns.length > 0) {
    towns.value.push(route.query.towns)
}

const minPrice = ref(Number.parseInt(route.query.min_price) || 0)
const maxPrice = ref(Number.parseInt(route.query.max_price) || 1000000000)
const minSize = ref(Number.parseInt(route.query.min_size) || 1)
const maxSize = ref(Number.parseInt(route.query.max_size) || 1000000000)
const minRooms = ref(Number.parseInt(route.query.min_rooms) || 1)
const maxRooms = ref(Number.parseInt(route.query.max_rooms) || 1000000000)

const query = ref("")

const serachBarStatus = ref(false)

const addTown = () => {
    towns.value.push(town.value)
    town.value = ""
}
const removeTown = (town) => {
    towns.value = towns.value.filter(t => t != town)
}
const makeQuery = () => {
    if (maxPrice.value < minPrice.value) {
        maxPrice.value, minPrice.value = minPrice.value, maxPrice.value
    }
    if (maxSize.value < minSize.value) {
        maxSize.value, minSize.value = minSize.value, maxSize.value
    }
    if (maxRooms.value < minRooms.value) {
        maxRooms.value, minRooms.value = minRooms.value, maxRooms.value
    }

    query.value = (
        `?skip=${skip.value}&limit=${limit.value}` +
        `&min_price=${minPrice.value}&max_price=${maxPrice.value}` +
        `&min_size=${minSize.value}&max_size=${maxSize.value}` +
        `&min_rooms=${minRooms.value}&max_rooms=${maxRooms.value}` +
        `&max=${max.value}`
    )

    console.log(query.value)

    towns.value.forEach(town => {
        query.value += `&towns=${town}`
    })

    return query.value
}
const getListDataset = async () => {
    const query = makeQuery()

    const response = await fetch(
        `/api/apartments${query}`, { method: "GET" }
    )
    const data = await response.json()

    dataset.value = data["data"]
    max.value = data["amount"]
    lastSkip.value = skip.value - limit.value
    skip.value += dataset.value.length
}
const search = async () => {
    skip.value = 0
    router.push(makeQuery())
}
const prevPage = async () => {
    skip.value = lastSkip.value
    router.push(makeQuery())
}
const nextPage = async () => {
    router.push(makeQuery())
}

getListDataset()
</script>

<template>
    <div class="container-fluid justify-content-start">
        <button class="btn btn-sm btn-primary nav-toggle" @click="serachBarStatus = !serachBarStatus"></button>
        <nav class="container-fluid justify-content-start" id="search-bar" v-if="serachBarStatus">
            <button class="btn btn-sm btn-danger nav-toggle" @click="serachBarStatus = !serachBarStatus"></button>
            <div class="mb-3">
                <div>
                    <label for="price-min">Minimal price</label>
                    <input class="form-control" id="price-min" min="0" max="1000000000" v-model="minPrice">
                </div>
                <div>
                    <label for="price-max">Maximum price</label>
                    <input class="form-control" id="price-max" min="0" max="1000000000" v-model="maxPrice">
                </div>
            </div>
            <div class="mb-3">
                <div>
                    <label for="size-min">Minimal size</label>
                    <input class="form-control" id="size-min" min="1" max="1000000000" v-model="minSize">
                </div>
                <div>
                    <label for="size-max">Maximum size</label>
                    <input class="form-control" id="size-max" min="1" max="1000000000" v-model="maxSize">
                </div>
            </div>
            <div class="mb-3">
                <div>
                    <label for="rooms-min">Minimal rooms amount</label>
                    <input class="form-control" id="rooms-min" min="1" max="1000000000" v-model="minRooms">
                </div>
                <div>
                    <label for="rooms-max">Maximum rooms amount</label>
                    <input class="form-control" id="rooms-max" min="1" max="1000000000" v-model="maxRooms">
                </div>
            </div>
            <div class="mb-3">
                <div>
                    <label for="towns-input">Towns</label>
                    <input class="form-control" id="towns-input" type="text" v-model="town">
                    <button class="btn btn-sm btn-success" @click="addTown">insert</button>
                </div>
                <div id="towns-container" v-for="town in towns">
                    <label>{{ town }}</label>
                    <button class="btn btn-sm btn-danger" @click="removeTown(town)">x</button>
                </div>
            </div>
            <button class="btn btn-sm btn-primary" @click="search">Search</button>
        </nav>
        <div class="container-fluid ad-view" v-for="data in dataset">
            <div class="row">
                <div class="col view-img">
                    <RouterLink :to="'/apartments/' + data._id + '?towns=' + towns">
                        <img class="view-img" :src="data.images[0]">
                    </RouterLink>
                </div>
                <div class="col">
                    <h2>{{ data.name }}</h2>
                    <h4>{{ data.location.city }}</h4>
                    <h4> Ціна: $ {{ data.price }} </h4>
                    <div>
                        <div>Розмір кінати: {{ data.size }} метрів квадратних</div>
                        <div>Кількість кімнат: {{ data.rooms }} кімната</div>
                    </div>
                </div>
            </div>
        </div>
        <div>
            <span v-if="skip > limit" @click="prevPage">prev</span>
            <span v-if="skip < max" @click="nextPage">next</span>
        </div>
    </div>
</template>

<style scoped>
.view-img {
    border: 1px solid gray;
    border-radius: 5px;
    max-width: 800px;
    max-height: 600px;
    width: 70%;
}
.view-img img {
    border: none;
    width: 100%;
    object-fit: contain;
}
.ad-view {
    margin-top: 10px;
}
.nav-toggle {
    border-radius: 50%;
    height: 25px;
    width: 25px;
    position: fixed;
    top: 0;
    right: 0;
}
#search-bar {
    background-color: white;
    border: 1px solid gray;
    width: 30%;
    position: fixed;
    top: 0;
    right: 0;
    overflow-y: auto;
    height: 100%;
}
</style>