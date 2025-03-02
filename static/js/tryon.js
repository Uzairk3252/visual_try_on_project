async function updatePose() {
    const response = await fetch('/pose');
    const data = await response.json();

    if (data.error) return;

    const keypoints = data.keypoints;
    const neck = data.neck;
    const leftWrist = data.left_wrist;
    const rightWrist = data.right_wrist;
    const leftElbow = data.left_elbow;
    const rightElbow = data.right_elbow;

    drawClothing(keypoints, neck, leftWrist, rightWrist, leftElbow, rightElbow);
}

function drawClothing(keypoints, neck, leftWrist, rightWrist, leftElbow, rightElbow) {
    if (!keypoints || !neck) return;

    const leftShoulder = keypoints[11];
    const rightShoulder = keypoints[12];

    // Calculate body scale
    const shoulderWidth = Math.abs(rightShoulder.x - leftShoulder.x) * canvas.width;
    const bodyHeight = Math.abs(leftWrist.y - leftShoulder.y) * canvas.height;

    // Adjust collar position slightly lower
    const clothingX = (neck.x * canvas.width) - (shoulderWidth / 2);
    const clothingY = (neck.y * canvas.height) - (bodyHeight / 4) + 20; // Moves collar down

    // Calculate sleeve positions
    let sleeveLeftX = leftElbow.x * canvas.width;
    let sleeveLeftY = leftElbow.y * canvas.height;
    let sleeveRightX = rightElbow.x * canvas.width;
    let sleeveRightY = rightElbow.y * canvas.height;

    let sleeveLeftEndX = leftWrist.x * canvas.width;
    let sleeveLeftEndY = leftWrist.y * canvas.height;
    let sleeveRightEndX = rightWrist.x * canvas.width;
    let sleeveRightEndY = rightWrist.y * canvas.height;

    // Rotate sleeves to match hand movement
    let leftAngle = Math.atan2(sleeveLeftEndY - sleeveLeftY, sleeveLeftEndX - sleeveLeftX);
    let rightAngle = Math.atan2(sleeveRightEndY - sleeveRightY, sleeveRightEndX - sleeveRightX);

    // Draw clothing
    ctx.drawImage(clothingImg, clothingX, clothingY, shoulderWidth * 1.5, bodyHeight * 1.5);

    // Draw sleeves (Rotate correctly)
    drawRotatedImage(leftSleeveImg, sleeveLeftX, sleeveLeftY, 40, 80, leftAngle);
    drawRotatedImage(rightSleeveImg, sleeveRightX, sleeveRightY, 40, 80, rightAngle);
}

// Function to rotate sleeves correctly
function drawRotatedImage(image, x, y, width, height, angle) {
    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(angle);
    ctx.drawImage(image, -width / 2, -height / 2, width, height);
    ctx.restore();
}

// Run pose updates every 100ms
setInterval(updatePose, 100);
