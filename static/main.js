const ID_INPUT_SEARCH = "input-search"
const ID_DIV_CONTENT_AREA = "content-area"
const ID_MODAL_DETAIL = "detail-modal"
const ID_MODAL_TITLE = "detail-modal-label"
const ID_MODAL_CONTENT = "detail-modal-content"
const ID_SELECT_SEARCH = "select-search"

const LOADING_HTML = '<div class="text-center"><img src="../static/img/dancing_duck.gif" width="300em" class="m-5"/></div>'

const SIM_THRESHOLD = 0.11
function get_base_url() {
    return "http://" + window.location.host + window.location.pathname
}

function search_enter(e) {
    if (e.key == "Enter") {
        search()
    }
}

function change_select() {
    var e = document.getElementById(ID_SELECT_SEARCH);
    console.log(e.value);

    search()
}

function search() {
    const search_str = document.getElementById(ID_INPUT_SEARCH).value
    const search_target = document.getElementById(ID_SELECT_SEARCH).value

    params = ["search=" + search_str, "target=" + search_target]
    window.location.href = get_base_url() + "?" + params.join("&")
}

function page_load() {
    const urlParams = new URLSearchParams(window.location.search);

    const search_str = urlParams.get("search")
    const search_target = urlParams.get("target") == null ? "name" : urlParams.get("target")

    if (search_str != null && search_str != "") {
        document.getElementById(ID_INPUT_SEARCH).value = search_str
        document.getElementById(ID_SELECT_SEARCH).value = search_target
        fetch_data(search_str, search_target)
    } else {
        document.getElementById(ID_DIV_CONTENT_AREA).innerHTML = `<div class="text-center py-4"><h5>Enter a search to start!</h5></div>`
    }
}

function fetch_data(search_string, search_target) {
    // Show loading animation
    document.getElementById(ID_DIV_CONTENT_AREA).innerHTML = LOADING_HTML

    // Fetch the data
    count = 10
    const request = new Request(`${get_base_url()}/api/search?query=${search_string.replace(" ", "%20")}&target=${search_target}&count=${count}`);
    fetch(request)
        .then((response) => response.text())
        .then((text) => {
            display_search_results(JSON.parse(text))
        });
}

function show_detail(id, name) {
    // Fill loading content   
    document.getElementById(ID_MODAL_TITLE).innerHTML = `<h1 class="modal-title fs-5">${name}</h1><small class="fs-6 fw-light">(${id})</small>`
    document.getElementById(ID_MODAL_CONTENT).innerHTML = LOADING_HTML
    show_detail_modal()

    // Fetch data
    const request = new Request(`${get_base_url()}/api/card?id=${id}`);
    fetch(request)
        .then((response) => response.text())
        .then((text) => {
            document.getElementById(ID_MODAL_CONTENT).innerHTML = render_modal_content(JSON.parse(text))
        });
}

function render_modal_content(card) {
    return `
    <div class="row">
        <div class="col-4">
            <img src="${card["img"]}" width="100%" class="bg-dark"/>
        </div>
        <div class="col-8">
            <table class="table table-sm">
  
                <tbody>
                    <tr>
                        <th>Name</th>
                        <td>${card["name"]}</td>
                    </tr>
                    <tr>
                        <th>Type</th>
                        <td>${card["type"]}</td>
                    </tr>
                    <tr>
                        <th>Set</th>
                        <td>${card["set"]}</td>
                    </tr>
                    <tr>
                        <th>Cost</th>
                        <td>${render_cost(card["mana_cost"], card["mana_val"])}</td>
                    </tr>
                    <tr>
                        <th>MTG Gatherer</th>
                        <td>Multiverse ID: ${card["id"]} - <a href="${card["url"]}" target="_blank">Original Entry</a></td>
                    </tr>
                    <tr>
                        <th>Artist</th>
                        <td>${card["artist"]}</td>
                    </tr>
                    <tr>
                        <th>Card Number</th>
                        <td>${card["card_num"]}</td>
                    </tr>
                    <tr>
                        <th>Text</th>
                        <td>${render_text(card["text"])}</td>
                    </tr>
                    <tr>
                        <th>Story</th>
                        <td>${render_story(card["story"])}</td>
                    </tr>
                </tbody>

            </table>
        </div>        
    </div>
    `
}

function render_cost(mana, cost) {
    if (mana == null) {
        return "/"
    }

    return `${render_mana_icons(mana, "16em")}<span class="ms-1">(${cost})</span>`
}

function render_text(text) {
    if (text == null) {
        return "/"
    }

    var ret_str = ""
    text.split("\r\n").forEach((str) => {
        ret_str += `<p class="m-0 p-0">${str}</p>`
    })

    return `<div class="d-flex flex-column gap-2">${render_mana_icons(ret_str, "16em")}</div>`
}

function render_story(story) {
    if (story == null) {
        return "/"
    }

    var ret_str = ""
    story.replace("—", "\r\n—").split("\r\n").forEach((str) => {
        ret_str += `<p class="m-0 p-0">${str}</p>`
    })

    return `<div class="d-flex flex-column gap-1"><i>${ret_str}</i></div>`
}

function show_detail_modal() {
    const detail_modal = new bootstrap.Modal(document.getElementById(ID_MODAL_DETAIL), {})
    detail_modal.show("")
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
    "Tap": "tap",
    "Colorless": "C",
    "Variable Colorless": "X"
}

function render_mana_icons(str, width = "20em") {
    if (str == null) {
        return "/"
    }

    var result = str

    for (const [key, value] of Object.entries(ICON_MAP)) {
        const html = `<img src="https://gatherer.wizards.com/Handlers/Image.ashx?size=medium&name=${value}&type=symbol" width="${width}"/>`
        result = result.replaceAll(`@${key}@`, html)
    }

    return result
}

function display_search_results(json_obj) {
    var html_str = ""

    json_obj.forEach(element => {

        if (element["sim"] >= SIM_THRESHOLD) {
            html_str += `<div class="d-flex p-3 bg-body-tertiary rounded shadow zoom cursor-pointer mt-4" onclick="show_detail(${element["id"]}, '${element["name"].replace("'", "\\'")}')">
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
