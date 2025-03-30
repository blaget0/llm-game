'use strict';

export const canvas = document.querySelector('.draw-area');
const ctx = canvas.getContext('2d');

const brushButton = document.querySelector('.brush-tool');
const eraserButton = document.querySelector('.eraser-tool');
const brushText = document.querySelector('.brush-size-wrapper p');
const brushColorButton = document.querySelector('.color-selection');
const brushSizeForm = document.querySelector('.brush-size-change');
const cleanButton = document.querySelector('.clean-all-tool');

let isDrawing = false;
let paintingMode = true;
let eraserMode = false;

brushText.innerHTML = 'Размер кисти';

window.onload = setCanvasSize
window.onresize = setCanvasSize;

let brushColor = '#000000';
ctx.strokeStyle = brushColor;
ctx.lineWidth = brushSizeForm.value;

ctx.fillStyle = 'white';
ctx.fillRect(0, 0, canvas.width, canvas.height);
ctx.fill();

function setCanvasSize() {
    let data = canvas.toDataURL();
    let width = document.documentElement.clientWidth;
    if (width < 430) {
        canvas.width = 300;
        canvas.height = 250;
    } else if (width < 650) {
        canvas.width = 400;
        canvas.height = 333;
    } else {
        canvas.width = 600;
        canvas.height = 500;
    }
    ctx.fillStyle = 'white';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fill();
    ctx.strokeStyle = brushColor;
    ctx.lineWidth = brushSizeForm.value;
}

function startDrawing(e) {
    let rect = canvas.getBoundingClientRect();
    isDrawing = true;
    let x = e.pageX - rect.left;
    let y = e.pageY - rect.top;
    ctx.beginPath();
    ctx.moveTo(x, y);
}

function stopDrawing() {
    isDrawing = false;	
}

function draw(e) {
    let rect = canvas.getBoundingClientRect();
    if (isDrawing) {
        let x = e.pageX - rect.left;
		let y = e.pageY - rect.top;
		ctx.lineTo(x, y);
		ctx.stroke();
    }
}

function startDrawingTouch(e) {
    const touch = e.touches[0];
    let rect = canvas.getBoundingClientRect();
    isDrawing = true;
    let x = touch.clientX - rect.left;
    let y = touch.clientY - rect.top;
    ctx.beginPath();
    ctx.moveTo(x, y);
}

function drawTouch(e) {
    let rect = canvas.getBoundingClientRect();
    if (isDrawing) {
        e.preventDefault();
        const touch = e.touches[0];
        let x = touch.clientX - rect.left;
		let y = touch.clientY - rect.top;
		ctx.lineTo(x, y);
		ctx.stroke();
    }
}

brushButton.addEventListener('click', function() {
    if (paintingMode) {
        return 
    } else {
        paintingMode = true;
        eraserMode = false;
        ctx.strokeStyle = brushColor;
        brushButton.style.backgroundColor = 'var(--bg-wood)';
        brushButton.style.backgroundPosition = 'center';
        brushButton.style.backgroundRepeat = 'no-repeat';
        eraserButton.style.backgroundColor = 'var(--bg-white)';
        eraserButton.style.backgroundPosition = 'center';
        eraserButton.style.backgroundRepeat = 'no-repeat';
        brushText.innerHTML = 'Размер кисти';
    }
});

eraserButton.addEventListener('click', function() {
    if (eraserMode) {
        return 
    } else {
        paintingMode = false;
        eraserMode = true;
        ctx.strokeStyle = 'white';
        brushButton.style.backgroundColor = 'var(--bg-white)';
        brushButton.style.backgroundPosition = 'center';
        brushButton.style.backgroundRepeat = 'no-repeat';
        eraserButton.style.backgroundColor = 'var(--bg-wood)';
        eraserButton.style.backgroundPosition = 'center';
        eraserButton.style.backgroundRepeat = 'no-repeat';
        brushText.innerHTML = 'Размер ластика';
    }
});

cleanButton.addEventListener('click', function() {
    ctx.fillStyle = 'white';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fill();
});

brushSizeForm.addEventListener('input', function(e) {
    ctx.lineWidth = e.target.value;
});

brushColorButton.addEventListener('input', function(e) {
    brushColor = e.target.value;
    ctx.strokeStyle = e.target.value;
});

canvas.onmousedown = startDrawing;
canvas.onmouseup = stopDrawing;
canvas.onmouseout = stopDrawing;
canvas.onmousemove = draw;

canvas.ontouchstart = startDrawingTouch;
canvas.ontouchmove = drawTouch;
canvas.ontouchend = stopDrawing;