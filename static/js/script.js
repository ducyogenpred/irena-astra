var map = L.map("map").setView([14.6474256, 121.0458555], 12);
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: "&copy; OpenStreetMap contributors",
}).addTo(map);

var currentLayer;

// Function to load a dataset
function loadDataset(dataset) {
  fetch("/geojson/" + dataset)
    .then((response) => response.json())
    .then((data) => {
      if (currentLayer) {
        map.removeLayer(currentLayer);
      }
      currentLayer = L.geoJSON(data).addTo(map);
    })
    .catch((error) => console.error("Error loading GeoJSON:", error));
}

loadDataset("hospitals");

document.getElementById("hospitalsBtn").addEventListener("click", function () {
  loadDataset("hospitals");
});
document.getElementById("fireBtn").addEventListener("click", function () {
  loadDataset("fire_stations");
});
document.getElementById("schoolsBtn").addEventListener("click", function () {
  loadDataset("schools");
});

const container = document.getElementsByClassName("wrapper_paddingLeft");
document.getElementsByClassName("btn-left").addEventListener("click", () => {
  container.scrollLeft -= 150;
});
document.getElementsByClassName("btn-right").addEventListener("click", () => {
  container.scrollLeft += 150;
});
