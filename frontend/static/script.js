// get a single random quote and update the quotes container with contents
function getRandomQuote() {
  endpoint = "/random-quote";
  xhttp = new XMLHttpRequest();
  xhttp.onload = function () {
    if (this.status == 200) {
      document.getElementById("quotes-container").innerHTML = this.responseText;
    }
  };
  xhttp.open("GET", endpoint, true);
  xhttp.send();
}

function getAllQuotes() {
  endpoint = "/quotes";
  xhttp = new XMLHttpRequest();
  xhttp.onload = function () {
    if (this.status == 200) {
      // reset contents of quotes-container
      document.getElementById("quotes-container").innerHTML = "";
      // parse received json body to list
      quotes = JSON.parse(this.responseText);
      // find the html container
      container = document.querySelector("#quotes-container");
      // create a ul tag
      ul = document.createElement("ul");
      // iterate over quotes and creat a li tag for each
      quotes.forEach(function (quote) {
        li = document.createElement("li");
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

function getHostnames() {
  endpoint = "/hostname";
  xhttp = new XMLHttpRequest();
  xhttp.onload = function () {
    if (this.status == 200) {
      data = JSON.parse(this.responseText);
      document.getElementById("backend_hostname").innerHTML = data.backend;
      document.getElementById("frontend_hostname").innerHTML = data.frontend;
    }
  };
  xhttp.open("GET", endpoint, true);
  xhttp.send();
}

// update the hostnames every second
getbackendinfo = setInterval(function () {
  getHostnames();
}, 1000);

function addQuote(e) {
  e.preventDefault();
  try {
    const params = {
      quote: document.querySelector("#quote").value,
    };

    xhttp = new XMLHttpRequest();
    xhttp.onload = function () {
      if (this.status == 200) {
        document.getElementById("quotes-container").innerHTML =
          this.responseText;
        document.querySelector("#quote").value = "";
      } else {
        document.getElementById(
          "output"
        ).innerHTML = `Error: ${this.status}, ${this.responseText}`;
      }
    };
    xhttp.open("POST", "/add-quote", true);
    xhttp.setRequestHeader("Content-type", "application/json");
    xhttp.send(JSON.stringify(params));
  } catch (e) {
    document.getElementById("quotes-container").innerHTML = e.message;
  }
  return false;
}
