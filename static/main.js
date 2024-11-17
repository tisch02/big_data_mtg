const ID_INPUT_SEARCH = "input-search"

function search_enter(e) {
    if (e.key == "Enter"){
        search()
    }    
}

function search() {
    
    const search_str = document.getElementById(ID_INPUT_SEARCH).value
    params = ["search=" + search_str]
    
    if (search_str.replace(" ","") == ""){
        window.location.href = "http://" + window.location.host + window.location.pathname
    }
    
    window.location.href = "http://" + window.location.host + window.location.pathname + "?" + params.join("&")
}

function page_load() {
    console.log("Page Load");
    const urlParams = new URLSearchParams(window.location.search);

    const search_str = urlParams.get("search")
    if (search_str != null){
        console.log("Fetch Data");
    }

    
    
    

}

console.log("Hallo, Welt!");
