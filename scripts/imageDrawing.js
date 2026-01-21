// Function to draw image to canvas. It should take a configuration object a
// name and a source
function updateCanvasImage(id, maxWidth, maxHeight) {

    const config = gridStackConfig[id];
    const url = config.imageUrl;
    const seqNumber = config.seqNumber;

    // Get the canvas element
    const canvasEl = document.getElementById(`canvas-${id}`);
    console.debug(`Updating canvas image for ${id}`, canvasEl);

    // Load the image to a temporary Image object
    const img = new Image();
    img.decoding = "async";

    img.onload = () => {
        console.debug(`Image loaded for canvas ${id}, drawing to canvas.`);

        // Need to adjust the canvas size based on maxWidth and maxHeight while
        // maintaining aspect ratio
        const aspectRatio = img.width / img.height;

        // All I want to do is maximize the image to fit within maxWidth and
        // maxHeight
        if (img.width / maxWidth >= img.height / maxHeight) {
            canvasEl.width = maxWidth;
            canvasEl.height = maxWidth / aspectRatio;
        } else {
            canvasEl.height = maxHeight;
            canvasEl.width = maxHeight * aspectRatio;
        }

        console.log(`Rendering at canvas size: width ${canvasEl.width}, height ${canvasEl.height}`);
        
        const ctx = canvasEl.getContext('2d');

        // Clear the canvas before drawing
        ctx.clearRect(0, 0, canvasEl.width, canvasEl.height);

        // Draw the image scaled to fit the canvas
        ctx.drawImage(img, 0, 0, canvasEl.width, canvasEl.height);
    };

    img.onerror = () => {
        console.error(`Failed to load image for canvas ${id}`, img.src);
    };

    console.debug(`Setting image source for canvas ${id} to ${withSequence(url, seqNumber)}`);
    img.src = withSequence(url, seqNumber);
}