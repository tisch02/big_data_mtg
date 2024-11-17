const ID_INPUT_SEARCH = "input-search"
const ID_DIV_CONTENT_AREA = "content-area"

const SIM_THRESHOLD = 0.15

function get_base_url() {
    return "http://" + window.location.host + window.location.pathname
}

function search_enter(e) {
    if (e.key == "Enter"){
        search()
    }    
}

function search() {
    
    const search_str = document.getElementById(ID_INPUT_SEARCH).value
    params = ["search=" + search_str]
    window.location.href = get_base_url() + "?" + params.join("&")
}

function page_load() {
    console.log("Page Load");
    const urlParams = new URLSearchParams(window.location.search);

    const search_str = urlParams.get("search")
    if (search_str != null && search_str != ""){
        document.getElementById(ID_INPUT_SEARCH).value = search_str
        fetch_data(search_str)
    }
}

function fetch_data(search_string){
    // Show loading animation
    const loading_html = '<div class="text-center"><img src="../static/img/dancing_duck.gif" width="300em" class="m-5"/></div>'
    document.getElementById(ID_DIV_CONTENT_AREA).innerHTML = loading_html

    // Fetch the data
    count = 10
    const request = new Request(`${get_base_url()}/api/search?query=${search_string.replace(" ", "%20")}&count=${count}`);
    fetch(request)
        .then((response) => response.text())
        .then((text) => {
            display_search_results(JSON.parse(text))                
    });
}

function show_detail(id) {
    console.log("Show Detail" + id);    
}

const ICON_MAP = {
    "1": "1",
    "2": "2",
    "3": "3",
    "4": "4",
    "5": "5",
    "6": "6",
    "7": "7",
    "8": "8",
    "9": "9",
    "10": "10",
    "11": "11",
    "12": "12",
    "13": "13",
    "14": "14",
    "15": "15",
    "16": "16",
    "Green": "G",
    "Blue": "U",
    "Red": "R",
    "Black": "B",
    "White": "W",
    "Tap": "tap"
}

function render_mana_icons(str) {
    if (str == null) {
        return "/"
    }            

    var result = str

    for (const [key, value] of Object.entries(ICON_MAP)) {
        const html = `<img src="https://gatherer.wizards.com/Handlers/Image.ashx?size=medium&name=${value}&type=symbol" width="20em"/>`
        result = result.replaceAll(`@${key}@`, html)
    }

    return result
}

function display_search_results(json_obj) {
    var html_str = ""

    json_obj.forEach(element => {

        if (element["sim"] >= SIM_THRESHOLD) {
            html_str += `<div class="d-flex p-3 bg-body-tertiary rounded shadow zoom cursor-pointer mt-4" onclick="show_detail(${element["id"]})">
                        <img src="${element["img"]}" width="100em" class="bg-dark"/>
                        <div class="flex-grow-1 mx-3">
                            <h5 class="mb-0">${element["name"]}</h5>
                            <p class="my-0">${element["type"]}</p>
                            <p class="my-0">${element["set"]}</p>
                            <h6 class="mt-3 mb-0">Mana Cost</h6>
                            <div>${render_mana_icons(element["mana_cost"])}</div>
                            </div>
                        <div class="align-self-center">
                            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="64" fill="currentColor" class="bi bi-chevron-compact-right align-self-center" viewBox="4 0 8 16">
                                <path fill-rule="evenodd" d="M6.776 1.553a.5.5 0 0 1 .671.223l3 6a.5.5 0 0 1 0 .448l-3 6a.5.5 0 1 1-.894-.448L9.44 8 6.553 2.224a.5.5 0 0 1 .223-.671"/>
                            </svg>
                        </div>
                    </div>`
        }
    });

    if (html_str == "") {
        html_str = `<div class="text-center py-4"><h5>Seems like there is no card that matches the search :/</h5></div>`
    }
    
    document.getElementById(ID_DIV_CONTENT_AREA).innerHTML = html_str
}
