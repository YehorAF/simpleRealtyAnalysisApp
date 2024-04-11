<script setup>
import { Chart } from 'chart.js/auto'
import { ref, shallowRef, onMounted } from 'vue'
import mapboxgl from 'mapbox-gl'
import mapboxSdk from '@mapbox/mapbox-sdk/services/geocoding'
import 'mapbox-gl/dist/mapbox-gl.css'

mapboxgl.accessToken = "pk.eyJ1IjoieWVob3JhZiIsImEiOiJjbHVhY2gzYjMwZzBvMm5xazJtd205cDJzIn0.4HXXbuq9F2OGrZvyEIosfQ"

const chartPriceRef = shallowRef(null)
const chartAmountRef = shallowRef(null)
const chartRoomsRef = shallowRef(null)
const chartSizeRef = shallowRef(null)
const mapRef = shallowRef(null)
const markerRef = ref([])
const dataset = ref([])
const apartments = ref([])
const townsQuery = ref("")

const props = defineProps(["query"])

const loadData = async (towns) => {
    let query = ""

    towns.forEach(element => {
        query += `&towns=${element}`
    })

    console.log(query)

    townsQuery.value = towns
    const response = await fetch(`/api/apartments?limit=100${query}`)
    const data = await response.json()

    return data["data"]
}
const selectData = async (event, element) => {
    if (element.length < 1) {
        return
    }
    const idx = element[0].index
    dataset.value[idx].selected = !dataset.value[idx].selected
    const borderColor = dataset.value[idx].selected ? "#27AE60" : "#36a2eb"

    chartPriceRef.value.data.datasets[0].borderColor[idx] = borderColor
    chartAmountRef.value.data.datasets[0].borderColor[idx] = borderColor
    chartSizeRef.value.data.datasets[0].borderColor[idx] = borderColor
    chartRoomsRef.value.data.datasets[0].borderColor[idx] = borderColor

    chartPriceRef.value.update()
    chartAmountRef.value.update()
    chartSizeRef.value.update()
    chartRoomsRef.value.update()

    const selectedTowns = dataset.value.filter(element => element.selected)
    const towns = []
    let data = []

    if (selectedTowns.length > 0) {
        selectedTowns.forEach(element => {
            towns.push(element._id)
        })

        data = await loadData(towns)
    }
    apartments.value = data

    // markerRef.value[idx].setColor(borderColor)
}
const getStatistic = async (query) => {
    const response = await fetch(
        `/api/statistic${query ? query : ""}`, {method: "GET"}
    )
    const data = await response.json()

    const xlabels = []
    const price = []
    const amount = []
    const rooms = []
    const size = []

    data["data"].forEach(element => {
        xlabels.push(element["_id"])
        price.push(element["price"])
        amount.push(element["amount"])
        rooms.push(element["rooms"])
        size.push(element["size"])
    })

    return [xlabels, price, amount, rooms, size, data["data"]]
}
const createChart = (xlabels, price, amount, rooms, size) => {
    const chartPrice = new Chart("chart-price", {
        type: "bar",
        data: {
            labels: xlabels,
            datasets: [{
                label: "Ціна",
                data: price,
                backgroundColor: (new Array(xlabels.length)).fill("#36a2eb"),
                borderColor: (new Array(xlabels.length)).fill("#36a2eb"),
                borderWidth: 3
            }]
        },
        options: {
            plugins: {
                title: {
                    display: true,
                    text: "Середня ціна"
                }
            },
            onClick: selectData
        }
    })
    const chartAmount = new Chart("chart-amount", {
        type: "bar",
        data: {
            labels: xlabels,
            datasets: [{
                label: "Кількість оголошень",
                data: amount,
                backgroundColor: (new Array(xlabels.length)).fill("#36a2eb"),
                borderColor: (new Array(xlabels.length)).fill("#36a2eb"),
                borderWidth: 3
            }]
        },
        options: {
            plugins: {
                title: {
                    display: true,
                    text: "Кількість оголошень"
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
                label: "Кількість кімнат",
                data: rooms,
                backgroundColor: (new Array(xlabels.length)).fill("#36a2eb"),
                borderColor: (new Array(xlabels.length)).fill("#36a2eb"),
                borderWidth: 3
            }]
        },
        options: {
            plugins: {
                title: {
                    display: true,
                    text: "Середня кількість кімнат"
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
                label: "Розмір",
                data: size,
                backgroundColor: (new Array(xlabels.length)).fill("#36a2eb"),
                borderColor: (new Array(xlabels.length)).fill("#36a2eb"),
                borderWidth: 3
            }]
        },
        options: {
            plugins: {
                title: {
                    display: true,
                    text: "Середній розмір нерухомості в м^2"
                }
            },
            onClick: selectData
        }
    })
    const mapboxClient = mapboxSdk({accessToken: mapboxgl.accessToken})

    const map = new mapboxgl.Map({
        container: "map",
        style: "mapbox://styles/mapbox/streets-v12",
        center: [30.51957, 50.4475747],
        zoom: 4,
    })
    const markers = []

    map.on("load", () => {
        xlabels.forEach(label => {
            mapboxClient.forwardGeocode({
                query: `${label}, Україна`,
                autocomplete: false,
                limit: 1
            }).send().then(response => {
                if (
                    response &&
                    response.body &&
                    response.body.features &&
                    response.body.features.length
                ) {
                    const feature = response.body.features[0]
                    console.log(label, feature.center)
                    const marker = new mapboxgl.Marker({"color": "#36a2eb"})

                    marker.setLngLat(feature.center).addTo(map)

                    markers.push(marker)
                }
            })
        })

        // const geojsonData = {
        //     type: "FeatureCollection",
        //     features: markers.map(marker => ({
        //         type: "Feature",
        //         geometry: {
        //             type: "Point",
        //             coordinates: marker.getLngLat().toArray()
        //         },
        //         properties: {
        //             color: "#36a2eb"
        //         }
        //     }))
        // }

        // map.addSource("markers", {
        //     "type": "geojson",
        //     "data": geojsonData
        // })

        // map.addLayer({
        //     id: "markers",
        //     type: "circle",
        //     source: "markers",
        //     paint: {
        //         "circle-radius": 8,
        //         "circle-color": ["get", "color"]
        //     }
        // })

        // map.on("click", "markers", (e) => {
        //     console.log("hello")
        //     const clickedFeature = e.features[0]
        //     if (clickedFeature.properties.color === "#36a2eb") {
        //       clickedFeature.properties.color = "#27AE60"
        //     } else {
        //       clickedFeature.properties.color = "#36a2eb"
        //     }
        
        //     map.getSource("markers").setData(geojsonData)
        // })
    })

    markerRef.value = markers

    return [chartPrice, chartAmount, chartRooms, chartSize, map]
}
onMounted(async () => {
    const [xlabels, price, amount, rooms, size, data] = await getStatistic(props.query)
    const [chartPrice, chartAmount, chartRooms, chartSize, map] = createChart(xlabels, price, amount, rooms, size)

    dataset.value = data

    chartPriceRef.value = chartPrice
    chartAmountRef.value = chartAmount
    chartRoomsRef.value = chartRooms
    chartSizeRef.value = chartSize
    mapRef.value = map
})
</script>

<template>
    <div class="chart-gallery">
        <div style="width: 100%; overflow-x: auto; overflow-y: hidden">
            <div style="width: 3000px; height: 800px">
                <canvas id="chart-price" height="500" width="0"></canvas>
            </div>
        </div>
        <div style="width: 100%; overflow-x: auto; overflow-y: hidden">
            <div style="width: 3000px; height: 800px">
                <canvas id="chart-amount" height="500" width="0"></canvas>
            </div>
        </div>
        <div style="width: 100%; overflow-x: auto; overflow-y: hidden">
            <div style="width: 3000px; height: 800px">
                <canvas id="chart-rooms" height="500" width="0"></canvas>
            </div>
        </div>
        <div style="width: 100%; overflow-x: auto; overflow-y: hidden">
            <div style="width: 3000px; height: 800px">
                <canvas id="chart-size" height="500" width="0"></canvas>
            </div>
        </div>
    </div>
    <div class="map-outliner">
        <div id="map"></div>
    </div>
    <div>
        <div v-for="data in apartments">
            <h4>{{ data.name }}</h4>
            <div>
                ID: <RouterLink :to="'/apartments/' + data._id + '?towns=' + townsQuery">{{ data._id }}</RouterLink>
            </div>
            <div>Ціна: $ {{ data.price }}</div>
            <div>Розмір: {{ data.size }}</div>
            <div>Кількість кімнат: {{ data.rooms }}</div>
            <div>Місто: {{ data.location.city }}</div>
        </div>
    </div>
</template>

<style scoped>
.chart-gallery {
    display: flex;
    flex-wrap: wrap;
}
.map-outliner {
    min-width: 800px;
    min-height:  600px;
}
#map {
    width: 100%;
    height: 100lh;
}
</style>