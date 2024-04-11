<script setup>
import {Chart} from 'chart.js/auto'
import {ref, shallowRef, onMounted} from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const apartmentIdRef = ref(route.params.apartmentId)

const showNav = ref(false)

const images = ref([])
const towns = ref([])
const name = ref("")
const town = ref("")
const price = ref("")
const size = ref("")
const rooms = ref("")
const description = ref("")
const link = ref("")
const salesman = ref("")
const salesmanPage = ref("")

const dataset = ref([])

const priceEpsRef = ref(0)
const sizeEpsRef = ref(0)
const roomsEpsRef = ref(0)
const useTown = ref(true)

const chartPriceRef = shallowRef(null) 
const chartSizeRef = shallowRef(null)
const chartRoomsRef = shallowRef(null)

const selectData = (event, element) => {
    if (element.length < 1) {
        return
    }
    const idx = element[0].index
    dataset.value[idx].selected = !dataset.value[idx].selected
    const borderColor = dataset.value[idx].selected ? "#27AE60" : "white"

    chartPriceRef.value.data.datasets[0].borderColor[idx] = borderColor
    chartSizeRef.value.data.datasets[0].borderColor[idx] = borderColor
    chartRoomsRef.value.data.datasets[0].borderColor[idx] = borderColor

    chartPriceRef.value.update()
    chartSizeRef.value.update()
    chartRoomsRef.value.update()
}
const getApartment = async (apartmentId) => {
    const response = await fetch(`/api/apartments/${apartmentId}`)
    const data = await response.json()

    return data["data"]
}
const compareApartments = async (
    town, price, size, rooms, towns = null, priceEps = 0, sizeEps = 0, roomsEps = 0, useTowns = true 
) => {
    let qeury = `?price=${price}&size=${size}&rooms=${rooms}&price_eps=${priceEps}&size_eps=${sizeEps}&rooms_eps=${roomsEps}`

    if (useTowns && towns && towns.length > 0) {
        towns.forEach(element => {
            qeury += `&towns=${element}`
        })
    } else if (useTowns) {
        qeury += `&towns=${town}`
    }

    const response = await fetch(`/api/compare${qeury}`, {method: "GET"})
    const data = await response.json()

    const xlabels = []
    const dprice = []
    const drooms = []
    const dsize = []

    data["data"].forEach(element => {
        xlabels.push(element["_id"])
        dprice.push(element["price"])
        drooms.push(element["rooms"])
        dsize.push(element["size"])
    })

    return [xlabels, dprice, drooms, dsize, data["data"]]
}
const setColors = (xlabels, apartmentId) => {
    const idx = xlabels.findIndex(element => element === apartmentId)
    const colors = new Array(xlabels.length).fill("#36a2eb")

    if (idx !== -1) {
        colors[idx] = "#ff6384"
    }

    return colors
}
const createCharts = (xlabels, dprice, drooms, dsize, apartmentId) => {
    const colors = setColors(xlabels, apartmentId)

    const chartPrice = new Chart("chart-price", {
        type: "bar",
        data: {
            labels: xlabels,
            datasets: [{
                label: "Ціна",
                data: dprice,
                backgroundColor: colors,
                borderColor: (new Array(colors.length)).fill("white"),
                borderWidth: 3
            }]
        },
        options: {
            plugins: {
                title: {
                    display: true,
                    text: "Порівняння за ціною"
                }
            },
            onClick: selectData
        }
    })
    const chartSize = new Chart("chart-size", {
        type: "bar",
        data: {
            labels: xlabels,
            datasets: [{
                label: "Розміри",
                data: dsize,
                backgroundColor: colors,
                borderColor: (new Array(colors.length)).fill("white"),
                borderWidth: 3
            }]
        },
        options: {
            plugins: {
                title: {
                    display: true,
                    text: "Порівняння за розміром"
                }
            },
            onClick: selectData
        }
    })
    const chartRooms = new Chart("chart-rooms", {
        type: "bar",
        data: {
            labels: xlabels,
            datasets: [{
                label: "Кімнати",
                data: drooms,
                backgroundColor: colors,
                borderColor: (new Array(colors.length)).fill("white"),
                borderWidth: 3
            }]
        },
        options: {
            plugins: {
                title: {
                    display: true,
                    text: "Порівняння за кількістю кімнат"
                }
            },
            onClick: selectData
        }
    })
    return [chartPrice, chartSize, chartRooms]
}
const updateData = async (priceEps, sizeEps, roomsEps, useTowns, apartmentId) => {
    const [xlabels, dprice, drooms, dsize, data] = await compareApartments(
        town.value, price.value, size.value, rooms.value, towns.value, priceEps, sizeEps, roomsEps, useTowns
    )
    dataset.value = data
    const colors = setColors(xlabels, apartmentId)

    chartPriceRef.value.data = {
        labels: xlabels,
        datasets: [{
            label: "Ціна",
            data: dprice,
            backgroundColor: colors,
            borderColor: (new Array(colors.length)).fill("white"),
            borderWidth: 3
        }]
    }
    chartPriceRef.value.update()

    chartSizeRef.value.data = {
        labels: xlabels,
        datasets: [{
            label: "Розміри",
            data: dsize,
            backgroundColor: colors,
            borderColor: (new Array(colors.length)).fill("white"),
            borderWidth: 3
        }]
    }
    chartSizeRef.value.update()

    chartRoomsRef.value.data = {
        labels: xlabels,
        datasets: [{
            label: "Кімнати",
            data: drooms,
            backgroundColor: colors,
            borderColor: (new Array(colors.length)).fill("white"),
            borderWidth: 3
        }]
    }
    chartRoomsRef.value.update()
}

onMounted(async () => {
    const response = await getApartment(apartmentIdRef.value)

    if (route.query.towns){
        towns.value = route.query.towns.split(",")
    }

    images.value = response["images"]
    name.value = response["name"]
    town.value = response["location"]["city"]
    price.value = response["price"]
    size.value = response["size"]
    rooms.value = response["rooms"]
    description.value = response["description"]
    link.value = response["link"]
    salesman.value = response["salesman"]
    salesmanPage.value = response["salesman_page"]

    const [xlabels, dprice, drooms, dsize, data] = await compareApartments(
        town.value, price.value, size.value, rooms.value, towns.value
    )
    dataset.value = data

    const [chartPrice, chartSize, chartRooms] = createCharts(xlabels, dprice, drooms, dsize, apartmentIdRef.value)
    chartPriceRef.value = chartPrice 
    chartSizeRef.value = chartSize 
    chartRoomsRef.value = chartRooms
})
</script>

<template>
    <div class="lght-container">
        <button class="btn btn-primary btn-sm nav-toggle" @click="showNav = !showNav"></button>
        <nav v-if="showNav">
            <button class="btn btn-danger btn-sm nav-toggle" @click="showNav = !showNav"></button>
            <div class="container-fluid">
                <div class="mb-3">
                    <label for="price-eps">Епсилон ціни</label>
                    <input class="form-control" id="price-eps" type="number" min="0" step="0.01" v-model="priceEpsRef">
                </div>
                <div>
                    <label for="size-eps">Епсилон розміру</label>
                    <input class="form-control" id="size-eps" type="number" min="0" step="0.01" v-model="sizeEpsRef">
                </div>
                <div>
                    <label for="rooms-eps">Епсилон кімнат</label>
                    <input class="form-control" id="rooms-eps" type="number" min="0" step="1" v-model="roomsEpsRef">
                </div>
                <div>
                    <input id="use-town" type="checkbox" v-model="useTown">
                    <label for="use-town">Шукати тільки у вказаних містах</label>
                </div>
                <button class="btn btn-sm btn-primary" @click="updateData(priceEpsRef, sizeEpsRef, roomsEpsRef, useTown, apartmentIdRef)">update</button>
            </div>
            <div class="container-fluid">
                <div class="ad-container" v-for="data in dataset" :class="{'selected': data.selected}">
                    <div class="layout" v-if="data.selected"></div>
                    <h4>{{ data.name }}</h4>
                    <div>
                        ID: <RouterLink :to="'/apartments/' + data._id + '?towns=' + towns">{{ data._id }}</RouterLink>
                    </div>
                    <div>Ціна: $ {{ data.price }}</div>
                    <div>Розмір: {{ data.size }}</div>
                    <div>Кількість кімнат: {{ data.rooms }}</div>
                    <div>Місто: {{ data.location.city }}</div>
                    <div class="layout" v-if="data.selected"></div>
                </div>
            </div>
        </nav>
        <main>
            <div class="lght-gallery">
                <img v-for="image in images" class="lght-img" :src="image">
            </div>
            <div class=" container-fluid">
                <h2><a :href="link">{{ name }}</a></h2>
                <h4>{{ town }}</h4>
                <h4> $ {{ price }} </h4>
                <div>
                    <div>Розмір кінати: {{ size }} метрів квадратних</div>
                    <div>Кількість кімнат: {{ rooms }} кімната</div>
                    <div>Продавець: <a :href="salesmanPage">{{ salesman }}</a></div>
                </div>
                <p>
                    {{ description }}
                </p>
            </div>
            <div class="chart-box">
                <canvas class="chart" id="chart-price"></canvas>
                <canvas class="chart" id="chart-size"></canvas>
                <canvas class="chart" id="chart-rooms"></canvas>
            </div>
        </main>
    </div>
</template>

<style>
/* .lght-container {
    display: block;
} */
.lght-gallery {
    display: flex;
    flex-wrap: inherit;
    overflow-x: auto;
    padding: 5px 0px 5px 0px;
    border-top: 1px grey solid;
    border-bottom: 1px grey solid;
}
.chart-box {
    display: flex;
    flex-wrap: inherit;
    overflow-x: auto;
    border-top: 1px grey solid;
    border-bottom: 1px grey solid;
}
.lght-img {
    max-width: 1000px;
    max-height: 800px;
    min-width: 500px;
    min-height: 300px;
    width: 60%;
    object-fit: contain;
    margin: 5px;
}
.chart {
    max-width: 1000px;
    max-height: 500px;
    margin: 5px;
}
.layout {
    border: 1px solid #27AE60;
}
.ad-container {
    margin: 5px 0 5px 0;
    border-top: 1px solid gray;
    border-bottom: 1px solid gray;
}
.selected {
    background-color: rgba(46, 204, 113, 0.3);
}
.nav-toggle {
    border-radius: 50%;
    height: 25px;
    width: 25px;
    position: fixed;
    top: 0;
    right: 0;
}
.lght-container main {
    width: auto;
}
.lght-container nav {
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