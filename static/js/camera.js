const video = document.getElementById("videoElement");
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");
const clothingSelection = document.getElementById("clothingSelection");
const categorySelection = document.getElementById("category");

// Automatically start the camera
navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => { video.srcObject = stream; })
    .catch(err => console.error("Camera access denied", err));

// Function to load clothing options based on category
function loadClothingOptions() {
    const category = categorySelection.value;
    clothingSelection.innerHTML = ""; // Clear previous options

    fetch(`/get_clothes?category=${category}`)
        .then(response => response.json())
        .then(data => {
            data.clothes.forEach(item => {
                const option = document.createElement("option");
                option.value = item;
                option.innerText = item;
                clothingSelection.appendChild(option);
            });
        })
        .catch(err => console.error("Error loading clothing options:", err));
}

// Load men's clothing by default
loadClothingOptions();

// Function to capture image and apply clothing
function captureAndTryOn() {
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const selectedCloth = clothingSelection.value;

    fetch('/tryon', {
        method: "POST",
        body: JSON.stringify({ clothing: selectedCloth }),
        headers: { "Content-Type": "application/json" }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            canvas.style.backgroundImage = `url('static/output/${data.result}')`;
        } else {
            alert("Try-on failed. Please try again.");
        }
    })
    .catch(err => console.error("Try-on error:", err));
}
