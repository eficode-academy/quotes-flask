// get a single random quote and update the quotes container with contents
function getRandomQuote() {
  endpoint = "/random-quote";
  xhttp = new XMLHttpRequest();
}

function getRandom() {
  get("/random-quote");
}

function getAll() {
  get_json("/quotes");
}

function getVersion(endpoint, element)
{
  make_call(endpoint, function() {
    if ( this.status == 200) {
      var json = JSON.parse(this.responseText);
      document.getElementById(element).innerHTML = json.version;
    }else{
      document.getElementById(element).innerHTML = "Error";
    }
  })
}

function getDatabaseVersion()
{
  getVersion("/database/version", "database_version");
}

function getBackendVersion()
{
  getVersion("/backend/version", "backend_version");
}

function getFrontendVersion()
{
  getVersion("/version", "frontend_version");
}

function make_call(endpoint, method)
{
  var xhr = new XMLHttpRequest();
  xhr.open("GET", endpoint, true);
  xhr.timeout = 200;
  xhr.onload = method;
  xhr.send();
}

function getHostnames(){
  var endpoint = "/hostname";
  var xhttp = new XMLHttpRequest();
  xhttp.onload = function () {
    if (this.status == 200) {
      var data= JSON.parse(this.responseText)
      document.getElementById("backend_hostname").innerHTML=data.backend
      document.getElementById("frontend_hostname").innerHTML=data.frontend
    } else {
      document.getElementById("backend_hostname").innerHTML="Error response"
      document.getElementById("frontend_hostname").innerHTML="Error response"
  };
  }
  xhttp.open("GET", endpoint, true);
  xhttp.timeout = 200;
  xhttp.ontimeout = function (e) {
    document.getElementById("backend_hostname").innerHTML="Timeout"
    document.getElementById("frontend_hostname").innerHTML="Timeout"
  };
  xhttp.send();
}
var periodicUpdates = setInterval(function() {
  getFrontendVersion();
  getBackendVersion();
  getDatabaseVersion();
}, 1000);

function get(endpoint) {
  var xhttp = new XMLHttpRequest();
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
updatePodHostnames = setInterval(function () {
  getHostnames();
}, 1000);

function updatePodNameRow(name, rowId, podNames) {
  document.getElementById(rowId).innerHTML = "";
  tr = document.querySelector("#" + rowId);
  pod_name_td = document.createElement("td");
  pod_name_td.textContent = name + ":";
  tr.appendChild(pod_name_td);

  podNames.forEach(function (pod) {
    console.log(pod);
    td = document.createElement("td");
    td.textContent = pod;
    td.className = "badge bg-success";
    tr.appendChild(td);
  });
}

function updatePodNameRowNoPodsFound(name, rowId) {
  document.getElementById(rowId).innerHTML = "";
  tr = document.querySelector("#" + rowId);
  pod_name_td = document.createElement("td");
  pod_name_td.textContent = name + ":";
  tr.appendChild(pod_name_td);

  no_pod_td = document.createElement("td");
  no_pod_td.textContent = "No pods found";
  no_pod_td.className = "badge bg-secondary";
  tr.appendChild(no_pod_td);
}

function getPodNames() {
  endpoint = "/pod-names";
  xhttp = new XMLHttpRequest();
  xhttp.onload = function () {
    if (this.status == 200) {
      data = JSON.parse(this.responseText);
      // if there is a message, there are no pod names
      if ("message" in data) {
        console.log("Message received when querying pod-names:");
        console.log(data.message);
        document.getElementById("application-status-message").innerHTML =
          data.message;
      } else {
        // otherwise get the pod names
        document.getElementById("application-status-message").innerHTML = ""; // set to nothing when no message
        console.log(data);
        console.log("Got pod names, updating webpage ...");

        // we talked with the frontend to get this request, so we assume
        // there will always be atleast one frontend pod
        updatePodNameRow("Frontend", "frontend-pod-names", data.frontend_pods);

        if (data.backend_pods.length === 0) {
          console.log("No backend pods found.");
          updatePodNameRowNoPodsFound("Backend", "backend-pod-names");
        } else {
          updatePodNameRow("Backend", "backend-pod-names", data.backend_pods);
        }

        if (data.postgres_pods.length === 0) {
          console.log("No database pods found.");
          updatePodNameRowNoPodsFound("Database", "database-pod-names");
        } else {
          updatePodNameRow(
            "Database",
            "database-pod-names",
            data.postgres_pods
          );
        }
      }
    }
  };
  xhttp.open("GET", endpoint, true);
  xhttp.send();
}

updatePodNamesTable = setInterval(function () {
  getPodNames();
}, 1000);

function switchView() {
  containerDiv = document.getElementById("container-hostname-view");
  if (containerDiv.style.display === "none") {
    containerDiv.style.display = "block";
  } else {
    containerDiv.style.display = "none";
  }

  k8sHostnameDiv = document.getElementById("k8s-view");
  if (k8sHostnameDiv.style.display === "none") {
    k8sHostnameDiv.style.display = "block";
  } else {
    k8sHostnameDiv.style.display = "none";
  }
}

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
