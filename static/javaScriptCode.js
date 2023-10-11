let plates = 0;


document.addEventListener('DOMContentLoaded', function() {
    plates = 0;
    const forms = document.querySelectorAll('.needs-validation')
    document.addEventListener('click', function(event) {
        if (event.target.id == "dish-add") {
            spawnPlates();
        } else if (event.target.id.includes("dish-remove")) {
            event.target.parentElement.parentElement.parentElement.remove();
        } else if (event.target.id.includes("star")) {
            setStars(event.target);
        } else if (event.target.id.includes("Img-button")) {
            updateImage(event.target);
        } else if (event.target.id.includes("refresh")) {
            refreshImage(event.target);
        } else if (event.target.id == "btn-order-items") {
            orderItems();
        } else if (event.target.id == "dataSearchBtn") {
            searchItems("search");
        } else if (event.target.id == "dataClearBtn") {
            searchItems("clear");
        } else if (event.target.id == "AdvSearchBtn") {
            advSearchItems("search");
        } else if (event.target.id == "AdvClearBtn") {
            advSearchItems("clear");
        }
    })
    document.addEventListener('change', function(event) {
        if (event.target.id == "placeExisting") {
            setExisting(event.target.value);
        } else if (event.target.id.includes("dishExisting")) {
            setDishExisting(event.target);
        }
    })

})

function setDishExisting(selected) {
    let selectedVal = selected.value;
    let dishIdNum = selected.id.match(/\d+/);
    dishIdNum = dishIdNum[0];
    console.log(dishIdNum);
    url = window.origin + "/existing/dish";
    let requestOptions = {
        method: "POST",
        headers: {
            "content-type": "application/json"
        },
        body: JSON.stringify({"id": selectedVal})
    }
    fetch(url, requestOptions)
        .then(response => response.json())
        .then(data => {
           data = data[0];
           data["dishCost"] = data["dishCost"] / 100;
           console.log(data);
            let elements = [...document.querySelectorAll(`[id^='${dishIdNum}dish']`)];
            elements.forEach((el) => {
                let newId = el.id.replace(/(\d+)/, "")
                console.log(newId)
                if (newId in data) {
                    el.value = data[newId];
                }
            });
            // set image automatically
            let buttonId = `${dishIdNum}dishImg-button`
            updateImage(document.getElementById(buttonId));

            // set stars
            buttonId = `${dishIdNum}dish-star${data["dishRating"]}`
            console.log(buttonId)
            let star = document.getElementById(buttonId);
            setStars(star);
        })
}


function setExisting(selectedVal) {

    url = window.origin + "/existing/place";
    let requestOptions = {
        method: "POST",
        headers: {
            "content-type": "application/json"
        },
        body: JSON.stringify({"id": selectedVal})
    }
    fetch(url, requestOptions)
        .then(response => response.json())
        .then(data => {
            // get all place elements, check if they in data, if so add data
            let elements = [...document.querySelectorAll("*[id^='place']")];
            elements.forEach((el) => {
                if (el.id in data["place"][0]) {
                    el.value = data.place[0][el.id];
                }
            });
            // set image automatically
            updateImage(document.querySelector("#placeImg-button"));

            // set stars
            let star = document.querySelector("#place-star" + data["place"][0]["placeRating"]);
            setStars(star);

            // set dish drop-down
            let dishDropDown = [...document.querySelectorAll("*[id^='dishExisting']")];
            dishDropDown.forEach((el) => {
                for (let i = 0; i < data.dishes.length; i++) {
                    let option = document.createElement("option");
                    option.text = data.dishes[i]["dishName"];
                    option.value = data.dishes[i]["dish_id"];
                    el.add(option);
                }
            });
        });
}


function spawnPlates() {
    plates++
    let new_div = document.querySelector("#dish").cloneNode(true);
    let elementsWithDish = [...new_div.querySelectorAll("*[id^='dish']")];
    elementsWithDish.forEach((el) => {
        el.id = plates + el.id;
        if (el.name != "") {
            el.name = plates + el.name;
        }
        if (el.id.includes("dishName") || el.id.includes("dishCuisine") || el.id.includes("dishCourse")) {
            el.required = true;
        }
    });
    new_div.setAttribute("id", plates + "dish");
    new_div.hidden = false;
    document.querySelector("#add-plates").appendChild(new_div);
    return;

}


function setStars(star) {
    //set all stars to blank
    let value = 5;
    let star_name = star.id.slice(0, -1);
    console.log(star_name)
    for (let i = 1; i <= value; i++) {
        let new_star = document.getElementById(star_name + i);
        new_star.style.color = "white";
    }
    value = star.id.at(-1);
    //set input to the star value selected
    let input = document.getElementById(star.id.slice(0, -6) + "Rating");
    console.log(star.id.slice(0, -6) + "Rating")
    console.log(input)
    input.setAttribute("value", value);
    //loop through stars and set those selected.
    for (let i = 1; i <= value; i++) {
        let new_star = document.getElementById(star_name + i);
        new_star.style.color = "#34AC60";
    }
    return;
}


function updateImage(button) {
    let request = new XMLHttpRequest();
    let img_input = document.getElementById(button.id.slice(0, -7));
    let img = document.getElementById(button.id.slice(0, -7) + "-actual");
    if (img_input.value == "") {
        return
    }
    request.open("GET", img_input.value, true);
    request.send();
    request.onload = () => {
        status = request.status;
        console.log(status);
        if (status == 200) {
            img.setAttribute("src", img_input.value);
        } else {
            img.setAttribute("src", "https://static.vecteezy.com/system/resources/previews/005/337/799/original/icon-image-not-found-free-vector.jpg");
            img_input.value = "";
        }
        return;
    }
    return;
}

function refreshImage(button) {
    let img = document.getElementById(button.id.slice(0, -8) + "-actual");
    let img_input = document.getElementById(button.id.slice(0, -8));
    img_input.value = "";
    if (button.id == "placeImg-refresh") {
        //refresh place image
        img.setAttribute("src", "https://media.istockphoto.com/id/1211547141/photo/modern-restaurant-interior-design.jpg?s=612x612&w=0&k=20&c=CvJmHwNNwfFzVjj1_cX9scwYsl4mnVO8XFPi0LQMTsw=");
        return;
    } else if (button.id == "mealImg-refresh") {
        //refresh meal image
        img.setAttribute("src", "https://media.istockphoto.com/id/1054319798/photo/group-of-happy-friends-having-breakfast-in-the-restaurant.jpg?s=612x612&w=0&k=20&c=rdb2gaIzr5n2eZthvK1B73LQa3yapubVD2AM_-SF50o=");
        return;
    } else if (button.id.includes("dishImg")) {
        //refresh dish image
        img.setAttribute("src", "https://media.istockphoto.com/id/1081422898/photo/pan-fried-duck.jpg?s=612x612&w=0&k=20&c=kzlrX7KJivvufQx9mLd-gMiMHR6lC2cgX009k9XO6VA=");
        return;
    }
}

function orderItems() {
    //get sorting type
    orderType = document.querySelector("#ordering").value;
    ascDesc = document.querySelector("#asc-desc").value;
    console.log(orderType);
    console.log(ascDesc);
    // create an array with the element id ordered then reorder the html elements using this
    //loop through all dish-section elements
    let elementOrder = [];
    let dishElements = [...document.querySelectorAll(".data-section")];
    dishElements.forEach((el) => {
        if (orderType == "rating") {
            //find rating elements
            let rating = el.querySelector("#rating").innerHTML;
            elementOrder.push([rating, el.id]);
        }
        if (orderType == "eaten") {
            //find times eaten elements
            let timesEaten = el.querySelector("#dishVisited").innerHTML;
            timesEaten = timesEaten.replace("Times eaten: ", "");
            elementOrder.push([timesEaten, el.id]);
        }
        if (orderType == "cost") {
            let cost = el.querySelector("#dishCostHidden").innerHTML;
            elementOrder.push([cost, el.id]);
        }
        if (orderType == "alpha") {
            let name = el.querySelector("#Name").innerHTML;
            elementOrder.push([name, el.id]);
        }
        if (orderType == "recent") {
            let date = el.querySelector("#Date").innerHTML;
            elementOrder.push([date, el.id]);
        }
        if (orderType == "visited") {
            let visited = el.querySelector("#placeVisited").innerHTML;
            visited = visited.replace("Times Visited: ", "");
            elementOrder.push([visited, el.id]);
        }
    });
    console.log(elementOrder);
    //sort array based on first index
    if (orderType == "alpha") {
        elementOrder.sort();
    } else {
        for (let i = 0; i < elementOrder.length; i++) {
            let array_location = i;
            for (let j = i + 1; j < elementOrder.length; j++) {
                if (parseInt(elementOrder[j][0]) < parseInt(elementOrder[array_location][0])) {
                    array_location = j;
                }
            }
            if (array_location != i) {
                //swap
                let temp = elementOrder[i];
                elementOrder[i] = elementOrder[array_location];
                elementOrder[array_location] = temp;
            }
        };
    }
    console.log(elementOrder);
    //then sort elements based on their order on array second index
    parent = document.querySelector("#main-data-section")
    if (ascDesc == "asc") {
        //loop through array
        for (let i = elementOrder.length - 1; i > -1; i--) {
            let id = elementOrder[i][1];
            //loop through dishElements
            dishElements.forEach((el) => {
                if (el.id == id) {
                    parent.appendChild(el);
                }
            });
        }
    } else {
        //descending
        for (let i = 0; i < elementOrder.length; i++) {
            let id = elementOrder[i][1];
            //loop through dishElements
            dishElements.forEach((el) => {
                if (el.id == id) {
                    parent.appendChild(el);
                }
            });
        }
    }
}

function searchItems(type) {
    let searchVal = document.querySelector("#dataSearch").value;
    searchVal.toLowerCase();
    let dataElements = [...document.querySelectorAll(".data-section")];
    console.log(dataElements.length);
    //check if search empty or clear
    if (searchVal == "" || type == "clear") {
        dataElements.forEach((el) => {
            el.hidden = false;
            document.querySelector("#dataSearch").value = "";
            document.querySelector("#searchEmpty").hidden = true;
        });
    } else {
        let hidden = 0;
        document.querySelector("#searchEmpty").hidden = true;
        //loop through dishElements
        dataElements.forEach((el) => {
            let text = el.innerText.toLowerCase();
            if (text.includes(searchVal)) {
                el.hidden = false;
            } else {
                el.hidden = true;
                hidden++
            }
        });
        //check if all hidden
        if (hidden == dataElements.length) {
            document.querySelector("#searchEmpty").hidden = false;
        }
    }
}

function advSearchItems(type) {
    // find all the relevant advanced search elements
    let searchElements = [...document.querySelectorAll(".advSearch")];
    let dataElements = [...document.querySelectorAll(".data-section")];
    if (type == "clear") {
        //clear the elements
        searchElements.forEach((el) => {
            if (el.id != "AdvSearchCostCurrency") {
                el.value = "";
            }
        })
        dataElements.forEach((el) => {
            el.hidden = false;
            document.querySelector("#searchEmpty").hidden = true;
        });
    } else {
        // search
        let hidden = 0;
        //loop through data elements
        dataElements.forEach((dataEl) => {
            let found = true;
            dataEl.hidden = false;
            //loop through search elements to check if match
            searchElements.forEach((searchEl) => {
                //if empty move on
                if (searchEl.value == "" || !found) {
                    return
                }
                //else run through search types
                //find matching data ELement and compare contents
                let compare = "";
                let dataVal = "";
                let searchVal = "";
                let searchValNum = 0;
                let numVal = 0;

                //cost
                if (searchEl.id == "advSearchCostMin") {
                    let element = dataEl.querySelector("[id$='CostHidden']")
                    numVal = parseInt(element.innerHTML);
                    searchValNum = parseInt(searchEl.value) * 10;
                    compare = "min";
                } else if (searchEl.id == "advSearchCostMax") {
                    let element = dataEl.querySelector("[id$='CostHidden']")
                    numVal = parseInt(element.innerHTML);
                    searchValNum = parseInt(searchEl.value) * 10;
                    compare = "max";
                }
                //rating
                else if (searchEl.id == "advSearchMinRating") {
                    let element = dataEl.querySelector("#rating")
                    numVal = parseInt(element.innerHTML);
                    searchValNum = parseInt(searchEl.value);
                    compare = "min";
                } else if (searchEl.id == "advSearchMaxRating") {
                    let element = dataEl.querySelector("#rating")
                    numVal = parseInt(element.innerHTML);
                    searchValNum = parseInt(searchEl.value);
                    compare = "max";
                } else {
                    /*
                    gets the id name, sets idName an array seperated by upper case letters,
                    then finds elements that end with the the last element in the array and gets the inner text
                    The element ids should always match the id of the search element
                     */
                    let idName = searchEl.id.match(/[A-Z][a-z]+/g);
                    console.log(idName)
                    console.log(`[id$=${idName[idName.length - 1]}]`)
                    dataVal = dataEl.querySelector(`[id$=${idName[idName.length - 1]}]`).innerText.toLowerCase().trim();
                    compare = "equals";
                    console.log(dataVal)
                }

                //equals compares
                if (compare == "equals") {
                    searchVal = searchEl.value.toLowerCase().trim()
                    if (!dataVal.includes(searchVal)) {
                        found = false;
                        return;
                    }
                }
                //range compares
                else if (compare == "min") {
                    if (numVal < searchValNum) {
                        found = false;
                        return;
                    }

                } else if (compare == "max") {
                    if (numVal > searchValNum) {
                        found = false;
                        return;
                    }
                }
            })

            if (found == false) {
                //hide element
                dataEl.hidden = true;
                hidden++;
            }
        })
        if (hidden == dataElements.length) {
            document.querySelector("#searchEmpty").hidden = false;
        }

    }
}