// Need a place to keep the configuration
// A configuration should have
// gridPosition: {x, y, w, h}
// id: string (dynamic)
// imageUrl: string
// seqNumber: string (dynamic)
const gridStackConfig = {};
let grid;

const SIZE_CONFIG = {
    'TV_WIDE_SMALL': { width: 5, height: 270 },
};

// We should use local storage to keep a consistent config over reloads
function loadGridStackConfigFromLocalStorage() {
    const storedConfig = localStorage.getItem(LOCAL_STORAGE_KEY);
    if (storedConfig) {
        Object.assign(gridStackConfig, JSON.parse(storedConfig));
    } else {
        console.log('No existing gridstack config found in local storage.');
        Object.assign(gridStackConfig, defaultGridStackConfig);
    }
}

function saveGridStackConfigToLocalStorage() {
    localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(gridStackConfig));
}

// Function to add a new gridstack item configuration
function addGridStackItemConfig(id, url, seqNumber, gridPosition) {
    // Grid position does not have to be initialized
    gridPosition = gridPosition ?? {x: 0, y: 0, w: 1, h: 1};
    
    gridStackConfig[id] = {
        id: id,
        imageUrl: url,
        seqNumber: seqNumber,
        gridPosition: gridPosition // Default position and size
    };
}

function renderGridStackItem(gridItemConfig) {

    // Title item special case
    if (gridItemConfig.id === 'TITLE') {
        const item = {
            x: gridItemConfig.gridPosition.x,
            y: gridItemConfig.gridPosition.y,
            w: gridItemConfig.gridPosition.w,
            h: gridItemConfig.gridPosition.h,
            content: gridItemConfig.content,
            id: `widget-${gridItemConfig.id}`
        };
        return item;
    }
    
    const content = `<canvas id="canvas-${gridItemConfig.id}"></canvas>`;
    const item = {
        x: gridItemConfig.gridPosition.x,
        y: gridItemConfig.gridPosition.y,
        w: gridItemConfig.gridPosition.w,
        h: gridItemConfig.gridPosition.h,
        content: content,
        id: `widget-${gridItemConfig.id}`
    };
    return item;
}

function initializeGridStack() {

    // Set the render function so we can use raw HTML instead of the sanitized
    // bs that *the man* wants you to use
    GridStack.renderCB = function(el, w) {
        el.innerHTML = w.content;
    };

    // Load any saved configuration
    loadGridStackConfigFromLocalStorage();

    // Grid ele
    const gridElement = document.querySelector('.grid-stack');
    
    grid = GridStack.init(opts={float: true});
    console.log('Gridstack initialized:', grid);

    // Watch add event
    grid.on('added', (event, nodes) => {

        
        console.log('New element(s) added:', nodes);
        nodes.forEach(node => {
            
            // Check if title is in the name
            if (node.id.includes('TITLE')) {
                console.log('Title widget added, skipping image draw.');
                return;
            }
            
            const widgetId = node.id;
            const configId = widgetId.replace('widget-', '');
            const widget = node.el.childNodes[0];
            const rect = widget.getBoundingClientRect();
            console.log('Widget added:', widgetId, 'Config ID:', configId, 'Size:', rect);

            // Draw the image
            updateCanvasImage(
                configId,
                rect.width,
                rect.height
            );
        });
    });
    
    // Watch resize event
    grid.on('resizestop', (event, element) => {

        // Check if title is in the name
        console.log('Element resized:', element.id);
        console.log('Element details:', element);
        if (element.gridstackNode.id.includes('TITLE')) {
            console.log('Title widget resized, skipping image draw.');

            // Save the updated stack
            saveGridStackConfigToLocalStorage();
            return;
        }
        
        const widget = element.childNodes[0];
        const node = element.gridstackNode;
        const rect = widget.getBoundingClientRect();
        const gridStackId = element.gridstackNode.id;
        const configId = gridStackId.replace('widget-', '');
        
        console.log('Grid units:', {w: node.w, h: node.h });
        console.log('Pixel size:', {width: rect.width, height: rect.height});

        // Resize the image
        updateCanvasImage(
            configId,
            rect.width,
            rect.height
        )
        
        console.debug('Element ID:', element.id);
        temp1 = element;

        // Update the configuration
        gridStackConfig[configId].gridPosition = {
            x: node.x,
            y: node.y,
            w: node.w,
            h: node.h
        };
        console.debug('Updated gridStackConfig:', gridStackConfig[configId]);
        
        // Save the updated stack
        saveGridStackConfigToLocalStorage();
    });

    // Watch move event
    grid.on('dragstop', (event, element) => {

        // Check if title is in the name
        console.log('Element resized:', element.id);
        console.log('Element details:', element);
        if (element.gridstackNode.id.includes('TITLE')) {
            console.log('Title widget resized, skipping image draw.');

            // Save the updated stack
            saveGridStackConfigToLocalStorage();
            return;
        }
        
        // Update the configuration
        const gridStackId = element.gridstackNode.id;
        const configId = gridStackId.replace('widget-', '');
        const node = element.gridstackNode;
        gridStackConfig[configId].gridPosition = {
            x: node.x,
            y: node.y,
            w: node.w,
            h: node.h,
        };
        console.debug('Updated gridStackConfig:', gridStackConfig[configId]);

        // Save the updated stack
        saveGridStackConfigToLocalStorage();
    });
        
    
    // Load all items from the configuration
    const items = [];
    for (const id in gridStackConfig) {
        items.push(renderGridStackItem(gridStackConfig[id]));
    }
    console.log('Loading gridstack items:', items);

    if (TV_SIZE in SIZE_CONFIG) {
        grid.column(SIZE_CONFIG[TV_SIZE].width);
        grid.cellHeight(SIZE_CONFIG[TV_SIZE].height);
    }
    grid.load(items);

}