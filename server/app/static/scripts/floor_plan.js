class ViewBox {
    constructor(svg) {
        this.svg = svg;

        this.initial = this.getAsObject(svg);
        this.y = this.initial.x;
        this.x = this.initial.y;
        this.width = this.initial.width;
        this.height = this.initial.height;
    }

    update() {
        this.svg.setAttribute(
            "viewBox",
            `${this.x} ${this.y} ${this.width} ${this.height}`
        );
    }

    getAsArray() {
        const viewBox = this.svg.getAttribute("viewBox").split(" ").map(Number);
        return viewBox;
    }

    getAsObject() {
        const [x, y, width, height] = this.getAsArray(this.svg);
        return { x, y, width, height };
    }

    getZoomLimit(width) {
        let result = 1;
        switch (true) {
            case width < this.initial.width * 0.25:
                result = 0.25;
                break;

            case width > this.initial.width * 1.25:
                result = 1.25;
                break;
        }

        return result;
    }

    isPositionWithinBounds() {
        return this.x < this.width * 1.1 || this.y < this.height * 1.1;
    }

    addWheelZoom() {
        this.svg.addEventListener(
            "wheel",
            (event) => {
                event.preventDefault();

                let scale = event.deltaY / 1000;
                let pt = new DOMPoint(event.clientX, event.clientY);
                // get wheeled position on svg element coordinate system
                pt = pt.matrixTransform(this.svg.getScreenCTM().inverse());

                // get pt.x as a proportion of width and pt.y as proportion of height
                let xPropW = (pt.x - this.x) / this.width;
                let yPropH = (pt.y - this.y) / this.height;

                // calc new width and height, new x2, y2 (using proportions and new width and height)
                let targeted = {};
                targeted.width = this.width + this.width * scale;
                targeted.height = this.height + this.height * scale;

                let zoomLimit = this.getZoomLimit(targeted.width);
                if (zoomLimit != 1) {
                    targeted.width = this.initial.width;
                    targeted.height = this.initial.height;
                }

                this.width = targeted.width * zoomLimit;
                this.height = targeted.height * zoomLimit;
                this.x = pt.x - xPropW * targeted.width * zoomLimit;
                this.y = pt.y - yPropH * targeted.height * zoomLimit;

                this.update();
            },
            { passive: false }
        );
    }

    addPanning() {
        let isDragging = false;

        this.svg.addEventListener("mousedown", () => {
            isDragging = true;
        });

        this.svg.addEventListener("mousemove", (event) => {
            if (!isDragging) {
                return;
            }

            let zoomScale = this.width / this.initial.width;
            let sensitivity = 3 * zoomScale;

            this.x -= event.movementX * sensitivity;
            this.y -= event.movementY * sensitivity;
            // console.log(this.x, this.width);
            this.update();
        });

        this.svg.addEventListener("mouseup", () => {
            isDragging = false;
        });
    }
}
