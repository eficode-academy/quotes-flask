function getRandom() {
    get("/random-quote");
}

function getAll() {
    get_json("/quotes");
}

function get(endpoint) {
    var xhttp = new XMLHttpRequest();
    xhttp.onload = function() {
        if (this.status == 200) {
            document.getElementById("quotes-container").innerHTML = this.responseText;
        }
    };
    xhttp.open("GET", endpoint, true);
    xhttp.send();
}

function get_json(endpoint) {
    var xhttp = new XMLHttpRequest();
    xhttp.onload = function() {
        if (this.status == 200) {
            // reset contents of quotes-container
            document.getElementById("quotes-container").innerHTML = "";
            // parse received json body to list
            var quotes = JSON.parse(this.responseText);
            // find the html container
            var container = document.querySelector('#quotes-container');
            // create a ul tag
            var ul = document.createElement('ul');
            // iterate over quotes and creat a li tag for each
            quotes.forEach(function (quote) {
                var li = document.createElement('li');
                li.textContent = quote;
                ul.appendChild(li);
            });
            // close ul tag
            container.appendChild(ul);
        }
    };
    xhttp.open("GET", endpoint, true);
    xhttp.send();
}

function addCookie(e) {
    e.preventDefault();
    try {

        const params = {
            quote: document.querySelector('#quote').value,
        }

        var xhttp = new XMLHttpRequest();
        xhttp.onload = function() {
            if (this.status == 200) {
                document.getElementById("quotes-container").innerHTML = this.responseText;
                document.querySelector('#quote').value = ""
            } else {
                document.getElementById("output").innerHTML =
                    `Error: ${this.status}, ${this.responseText}`
            }
        };
        xhttp.open("POST", "/add-quote", true);
        xhttp.setRequestHeader('Content-type', 'application/json');
        xhttp.send(JSON.stringify(params));
    } catch (e) {
        document.getElementById("quotes-container").innerHTML = e.message;
    }
    return false;
}
