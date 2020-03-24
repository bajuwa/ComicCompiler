// ==UserScript==
// @name         ManDL (Manhua Downloader)
// @namespace    http://tampermonkey.net/
// @version      0.2
// @description  Downloads all images already loaded in to the page with a specific partial-source match
// @author       bajuwa
// @include *://ac.qq.com/ComicView/index/*
// @include *://*.kuaikanmanhua.com/web/comic/*
// @grant        GM_download
// @grant        GM_setValue
// @grant        GM_getValue
// @require      http://code.jquery.com/jquery-latest.js
// ==/UserScript==

var FILE_NAME_PREFIX = GM_getValue("MANDL_FILE_NAME_PREFIX", "image");
var FILE_EXTENSION = GM_getValue("MANDL_FILE_EXTENSION", ".jpg");
var NUM_OF_IMAGES_TO_SKIP = GM_getValue("MANDL_NUM_OF_IMAGES_TO_SKIP", 0);
var DOWNLOAD_ITERATION_DELAY = GM_getValue("MANDL_DOWNLOAD_ITERATION_DELAY", 200);
var AUTOSCROLL_PIXELS = GM_getValue("MANDL_AUTOSCROLL_PIXELS", 1000);
var AUTOSCROLL_MS_INTERVAL = GM_getValue("MANDL_AUTOSCROLL_MS_INTERVAL", 200);

var ELEMENT_ID_CONFIG_PANEL = "manDlConfigPanel";

(function() {
    'use strict';
    setupConfigPanel();
    console.log("ManDL - Ready!");
})();

function setupConfigPanel() {
    // Create a button to trigger download
    $('<button>Scrape</button>').click(function(){
        $("#"+ELEMENT_ID_CONFIG_PANEL).show();
    }).css({
        "position":"fixed",
        "right":"0",
        "top":"0",
        "z-index":"100"
    }).appendTo($("body"));

    // Create a div to hold all the configurations
    var configPanel = $('<div>').attr('id',ELEMENT_ID_CONFIG_PANEL).appendTo($('body')).css({
        "position":"fixed",
        "z-index":"101",
        "top":"0",
        "right":"0",
        "background":"black",
        "color":"white",
        "font-weight":"bold",
        "text-align":"left",
        "display":"none"
    });

    var configTable = $("<table>").appendTo(configPanel);
    addConfigOptions(configTable, "File Name Prefix:", FILE_NAME_PREFIX, value => {FILE_NAME_PREFIX = value; GM_setValue("MANDL_FILE_NAME_PREFIX", value)});
    addConfigOptions(configTable, "File Extension:", FILE_EXTENSION, value => {FILE_EXTENSION = value; GM_setValue("MANDL_FILE_EXTENSION", value)});
    addConfigOptions(configTable, "Skip First N Pages:", NUM_OF_IMAGES_TO_SKIP, value => {NUM_OF_IMAGES_TO_SKIP = value; GM_setValue("MANDL_NUM_OF_IMAGES_TO_SKIP", value)});
    addConfigOptions(configTable, "MS between file DLs:", DOWNLOAD_ITERATION_DELAY, value => {DOWNLOAD_ITERATION_DELAY = value; GM_setValue("MANDL_DOWNLOAD_ITERATION_DELAY", value)});
    addConfigOptions(configTable, "Scroll Pixels:", AUTOSCROLL_PIXELS, value => {AUTOSCROLL_PIXELS = value; GM_setValue("MANDL_AUTOSCROLL_PIXELS", value)});
    addConfigOptions(configTable, "Scroll MS Delay:", AUTOSCROLL_MS_INTERVAL, value => {AUTOSCROLL_MS_INTERVAL = value; GM_setValue("MANDL_AUTOSCROLL_MS_INTERVAL", value)});

    // Create a button to trigger automatic scroll to bottom of page (for lazy loaded images)
    $('<button>Auto-Scroll</button>').click(function(){
        scrollToBottom();
    }).appendTo(configPanel);

    // Create a button to trigger download
    $('<button>Download</button>').click(function(){
        downloadImages();
    }).appendTo(configPanel);

    // Create a button to close panel
    $('<button>Close</button>').click(function(){
        $("#"+ELEMENT_ID_CONFIG_PANEL).hide();
    }).appendTo(configPanel);
}

function addConfigOptions(parentElement, optionTitle, defaultValue, consumer) {
    var row = $("<tr>").appendTo(parentElement);
    $("<td>").appendTo(row).append($("<span>"+optionTitle+"</span>"));
    $("<td>").appendTo(row).append(
        $("<input type=text value='" + defaultValue + "'></input>").on("change paste keyup", function() {
            consumer($(this).val());
        })
    );
};

function scrollToBottom() {
    console.log("Scroll with configurations...");
    console.log("AutoScroll pixels: " + AUTOSCROLL_PIXELS);
    console.log("AutoScroll MS interval: " + AUTOSCROLL_MS_INTERVAL);
    var interval = setInterval( function(){
            window.scrollBy(0, AUTOSCROLL_PIXELS);
    }, AUTOSCROLL_MS_INTERVAL);
}

function downloadImages() {
    console.log("Download with configurations...");
    console.log("File name prefix: " + FILE_NAME_PREFIX);
    console.log("File extension: " + FILE_EXTENSION);
    console.log("Skip first N pages: " + NUM_OF_IMAGES_TO_SKIP);
    console.log("MS between file downloads: " + DOWNLOAD_ITERATION_DELAY);

    var imagesToDownload = findImagesFromSource(window.location.href);
    console.log("imagesToDownload count: " + imagesToDownload.length);

    var time = DOWNLOAD_ITERATION_DELAY;
    imagesToDownload.each(function(index, element) {
        setTimeout( function(){
            if (index < NUM_OF_IMAGES_TO_SKIP) {
                console.log("Skipping image with src: " + element.src);
            } else {
                GM_download(element.src, FILE_NAME_PREFIX + pad(index, 3) + FILE_EXTENSION);
            }
        }, time);
        time += DOWNLOAD_ITERATION_DELAY;
    });
}

function findImagesFromSource(sourceHref) {
    if (sourceHref.includes("pufeimanhua")) {
        return $("img.comicimg");
    } else if (sourceHref.includes("kuaikanmanhua")) {
        return $(".comicDetails img[src*=\"kkmh.com/image\"]");
    } else if (sourceHref.includes("ac.qq")) {
        return $("img[src*=\"manhua_detail\"]");
    } else {
        console.log("WARNING: Could not determine appropriate scraping criteria, downloading all images");
        return $("img[src^=jpg]");
    }
}

function pad(n, width, z) {
  z = z || '0';
  n = n + '';
  return n.length >= width ? n : new Array(width - n.length + 1).join(z) + n;
}
