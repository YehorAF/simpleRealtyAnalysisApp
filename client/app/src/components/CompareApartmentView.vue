<script setup>
import { Chart } from 'chart.js/auto'
import { ref, shallowRef, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const currentTown = ref("")
const townList = ref([])
const selectedTowns = ref([])
const wishPrice = ref(20000)
const apartmentSize = ref(20)
const roomNumber = ref(1)

const clusterId = ref(0)
const optimalPrice = ref(0)
const avgPrice = ref(0)
const avgSize = ref(0)
const dataset = ref([])

const priceChartRef = shallowRef(null)
const sizeChartRef = shallowRef(null)
const roomsChartRef = shallowRef(null)

const addTown = (town) => {
    if (selectedTowns.value.findIndex(element => element === town) !== -1) {
        return
    }
    selectedTowns.value.push(town)
}
const removeTown = (town) => {
    selectedTowns.value = selectedTowns.value.filter(element => element !== town)
}
const compareWithSimilar = async (price, size, rooms, towns) => {
    let response = await fetch(
        `/api/predict?price=${price}&size=${size}`, {method: "GET"}
    )
    let data = await response.json()
    clusterId.value = data["data"]["cluster_id"]
    optimalPrice.value = data["data"]["optimal_price"]
    avgSize.value = data["data"]["avg_size"]
    avgPrice.value = data["data"]["avg_price"]

    let townsQuery = ""

    if (Array.isArray(towns) && towns.length > 0) {
        towns.forEach(element => {
            townsQuery += `&towns=${element}`
        })
    }
    response = await fetch(
        `/api/compare?price=${price}&size=${size}&rooms=${rooms}&cluster_id=${clusterId.value}` +
        `&price_eps=${price / 4}&size_eps=${size / 2}&rooms_eps=120&limit=100${townsQuery}`, 
        {method: "GET"}
    )
    data = await response.json()
    dataset.value = data["data"]
    updateData(dataset.value)
}

const selectData = (event, element) => {
    if (element.length < 1) {
        return
    }
    const idx = element[0].index
    dataset.value[idx].selected = !dataset.value[idx].selected
    const borderColor = dataset.value[idx].selected ? "#27AE60" : "white"

    priceChartRef.value.data.datasets[0].borderColor[idx] = borderColor
    sizeChartRef.value.data.datasets[0].borderColor[idx] = borderColor
    roomsChartRef.value.data.datasets[0].borderColor[idx] = borderColor

    priceChartRef.value.update()
    sizeChartRef.value.update()
    roomsChartRef.value.update()
}
const setColors = (xlabels, apartmentId) => {
    const idx = xlabels.findIndex(element => element === apartmentId)
    const colors = new Array(xlabels.length).fill("#36a2eb")

    if (idx !== -1) {
        colors[idx] = "#ff6384"
    }

    return colors
}
const createCharts = (
    xlabels = [], 
    dprice = [], 
    drooms = [], 
    dsize = [], 
    apartmentId = NaN
) => {
    const colors = setColors(xlabels, apartmentId)

    const chartPrice = new Chart("price-chart", {
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
    const chartSize = new Chart("size-chart", {
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
    const chartRooms = new Chart("rooms-chart", {
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
const updateData = (data) => {
    const xlabels = []
    const dprice = []
    const drooms = []
    const dsize = []

    data.forEach(element => {
        xlabels.push(element["_id"])
        dprice.push(element["price"])
        drooms.push(element["rooms"])
        dsize.push(element["size"])
    })
    const colors = setColors(xlabels)

    priceChartRef.value.data = {
        labels: xlabels,
        datasets: [{
            label: "Ціна",
            data: dprice,
            backgroundColor: colors,
            borderColor: (new Array(colors.length)).fill("white"),
            borderWidth: 3
        }]
    }
    priceChartRef.value.update()

    sizeChartRef.value.data = {
        labels: xlabels,
        datasets: [{
            label: "Розмір",
            data: dsize,
            backgroundColor: colors,
            borderColor: (new Array(colors.length)).fill("white"),
            borderWidth: 3
        }]
    }
    sizeChartRef.value.update()

    roomsChartRef.value.data = {
        labels: xlabels,
        datasets: [{
            label: "Кімнати",
            data: drooms,
            backgroundColor: colors,
            borderColor: (new Array(colors.length)).fill("white"),
            borderWidth: 3
        }]
    }
    roomsChartRef.value.update()
}
onMounted(() => {
    const [chartPrice, chartSize, chartRooms] = createCharts()
    priceChartRef.value = chartPrice 
    sizeChartRef.value = chartSize 
    roomsChartRef.value = chartRooms
})
</script>

<template>
    <div>
        <div class="data-info">
            <nav>
                <div class="container-fluid">
                    <label for="wish-price">Бажана ціна</label>
                    <input class="form-control" id="wish-price" type="number" placeholder="Бажана ціна" min="20000" max="130000" step="0.01" v-model="wishPrice">
                </div>
                <div class="container-fluid">
                    <label for="size">Розмір</label>
                    <input class="form-control" id="size" type="number" placeholder="Розмір" min="20" max="120" step="0.1" v-model="apartmentSize">
                </div>
                <div class="container-fluid">
                    <label for="rooms">Кількість кімнат</label>
                    <input class="form-control" id="rooms" type="number" placeholder="Кількість кімнат" min="1" max="120" step="1" v-model="roomNumber">
                </div>
                <div class="container-fluid">
                    <label for="town">Порівнювати з квартирами в містах</label>
                    <input class="form-control" id="town" placeholder="Місто" v-model="currentTown">
                    <button class="btn btn-success btn-sm" @click="addTown(currentTown)">Додати</button>
                    <button class="btn btn-primary btn-sm" @click="compareWithSimilar(wishPrice, apartmentSize, roomNumber, selectedTowns)">Шукати</button>
                    <div>
                        <div v-for="town in selectedTowns">
                            {{ town }}<button class="btn btn-danger btn-sm" @click="removeTown(town)">x</button>
                        </div>
                    </div>
                </div>
            </nav>
            <div :hidden="dataset.length === 0">
                <div class="container-fluid">Оптимальна ціна: {{ optimalPrice }}</div>
                <div class="container-fluid">Середня ціна в групі: {{ avgPrice }}</div>
                <div class="container-fluid">Середній розмір: {{ avgSize }}</div>
                <div class="chart-box">
                    <canvas class="chart" id="price-chart"></canvas>
                    <canvas class="chart" id="size-chart"></canvas>
                    <canvas class="chart" id="rooms-chart"></canvas>
                </div>
            </div>
        </div>
        <div v-if="dataset.length > 0" class="apartmnet-list">
            <div class="row ad-container" v-for="data in dataset" :class="{'selected': data.selected}">
                <div class="layout" v-if="data.selected"></div>
                <div class="col view-img">
                    <RouterLink :to="'/apartments/' + data._id">
                        <img :src="data.images[0]">
                    </RouterLink>
                </div>
                <div class="col">
                    <h2>{{ data.name }}</h2>
                    <h4>{{ data.location.city }}</h4>
                    <h4> Ціна: $ {{ data.price }} </h4>
                    <div>
                        <div>Розмір кінати: {{ data.size }} метрів квадратних</div>
                        <div>Кількість кімнат: {{ data.rooms }} кімнат</div>
                    </div>
                </div>
                <div class="layout" v-if="data.selected"></div>
            </div>
        </div>
    </div>
</template>

<style>
.chart-box {
    display: flex;
    flex-wrap: inherit;
    overflow-x: auto;
    border-top: 1px grey solid;
    border-bottom: 1px grey solid;
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
.view-img {
    max-width: 600px;
    max-height: 400px;
}
.view-img img {
    max-width: 600px;
    max-height: 400px;
    object-fit: contain;
}
</style>