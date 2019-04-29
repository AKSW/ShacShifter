

class StringSupplier:
    """Supplier for long Strings"""

    header = """<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/flatpickr/dist/flatpickr.min.css">
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/flatpickr"></script>
<script src="https://bowercdn.net/c/urijs-1.19.1/src/URI.min.js"></script>
<form action="">
SPARQL Endpoint <br>
<input type="text" name="endpoint" value="{}"><br>
Ressource IRI <br>
<input type="text" name="ressourceIRI" value="{}"><br>
Graph <br>
<input type="text" name="namedGraph" value="{}"><br>"""

    headerTargetClassSelect = """Select Targetclass<br>
<select id="targetClass">"""

    headerTargetOption = """<option value="{target}">{target}</option>"""

    headerTargetClassSelectClose = """</select><br>"""

    headerTargetObjectsOfSelect = """Select Predicate and Subject(sh:targetObjectsOf)<br>
<select id="targetObjectsOf">"""

    headerTargetObjectsOfSelectClose ="""</select><br>
<input type="text" name="targetObjectsOfSubject"><br>"""

    headerTargetSubjectsOfSelect = """Select Predicate and Object(sh:targetSubjectsOf<br>
<select id="targetSubjectsOf">"""

    headerTargetSubjectsOfSelectClose = """</select><br>
<input type="text" name="targetSubjectsOfObject"><br>"""

    submit = """<br>
<input type="button" id="submitbutton" onclick="sendData(this.form)" value="Submit" disabled>
</form>"""

    script = """
<script>
// not the same as date, always has the timezone part and it can only be 0
$(".date").flatpickr({dateFormat: "Z"});
// no timezone atm for most types
$(".time").flatpickr({enableTime: true, dateFormat: "H:i:S"});
$(".dateTime").flatpickr({enableTime: true, dateFormat: "Z"});
$(".gYearMonth").flatpickr({dateFormat: "Y-M"});
$(".gYear").flatpickr({dateFormat: "Y"});
$(".gMonthDay").flatpickr({dateFormat: "M-D"});
$(".gDay").flatpickr({dateFormat: "D"});
$(".gMonth").flatpickr({dateFormat: "M"});
if(typeof(String.prototype.trim) === "undefined")
{
    String.prototype.trim = function()
    {
        return String(this).replace(/^\\s+|\\s+$/g, '');
    };
}

function textfieldAdd(id) {
    var ancestor = document.getElementById(id),
    descendents = ancestor.getElementsByTagName('div');
    if(ancestor.dataset.max > 0 && descendents.length >= ancestor.dataset.max) {
        return;
    }
    var e, d, type, disableChoice, checked1, checked2, replacements;
    counter = descendents.length + 1;
    type = ancestor.dataset.type;
    if(type != "") {
        disableChoice = "disabled"
    }
    else {
        disableChoice = ""
    }
    if(disableChoice == "disabled"){
        checked1 = "";
        checked2 = "checked";
    }
    else {
        checked1 = "checked";
        checked2 = "";
    }
    pattern = '"' + ancestor.dataset.pattern + '"'
    jsclass = '"' + substr(ancestor.dataset.type.lastIndexOf('#') + 1) + '"'
    replacements = {
    "%ID%": id + counter,
    "%BID%": id,
    "%CHOICE%": disableChoice,
    "%CHECKED1%": checked1,
    "%CHECKED2%": checked2,
    "%PATTERN%": pattern,
    "%CLASS%": jsclass};
    e = document.createElement('div');
    e.setAttribute('id', id + counter.toString());
    d = [
    '<input type="text" name="%ID%" pattern=%PATTERN% class=%CLASS% onkeyup="checkFormValidity(this.parentElement)" onchange="checkFormValidity(this.parentElement)">',
    '<input type="radio" name="%ID%radio" %CHOICE% value="iri" onclick="checkFormValidity(this.parentElement)" %CHECKED1%>IRI',
    '<input type="radio" name="%ID%radio" %CHOICE% value="literal" onclick="checkFormValidity(this.parentElement)" %CHECKED2%>Literal',
    '<button type="button"',
    'onclick="textfieldDel(\\'%BID%\\', this.parentElement)">-</button>',
    '<br>'].join('\\n');
    d = d.replace(/%\\w+%/g, function(all) {
    return replacements[all] || all;});
    e.innerHTML = d;
    ancestor.appendChild(e);
    checkFormValidity(e);
}

function textfieldDel(id, delDiv){
    var ancestor = document.getElementById(id),
    descendents = ancestor.getElementsByTagName('div'),
    min = ancestor.dataset.min;
    if(descendents.length <= min){
        // consider sending a message why
        return;
    }
    ancestor.removeChild(delDiv);
    fixIdValues(id)
    checkMainDivValidity(ancestor)
}

function fixIdValues(id){
    var ancestor = document.getElementById(id),
    descendents = ancestor.getElementsByTagName('div');
    for (var i = 0; i < descendents.length; i++) {
        descendents[i].id = id + (i+1).toString();
        descendents[i].children[0].name = id + (i+1).toString();
        descendents[i].children[1].name = id + (i+1).toString() + "radio";
        descendents[i].children[2].name = id + (i+1).toString() + "radio";
    }
}

function sendData(form){
    if(form.endpoint.value.trim() === "" || form.ressourceIRI.value.trim() === "") {
        return;
    }
    //cant check for urls properly all regex solutions seem to be bad, use jquery? >only literals
    var triples = "",
    query = "",
    endpointURI = new URI(form.endpoint.value.trim()),
    ressourceURI = new URI(form.ressourceIRI.value.trim()),
    namedGraphURI = new URI(form.namedGraph.value.trim());
    if(!endpointURI.is("url") || !(ressourceURI.is("url") || ressourceURI.is("urn"))){
        return;
    }
    if(!form.namedGraph.value.trim() === "" && !namedGraphURI.is("url")){
        return;
    }
    if(form.targetClass != undefined) {
        triples += '<' + form.ressourceIRI.value.trim() + '> <http://www.w3.org/2000/01/rdf-schema#class> <' + form.targetClass.value.trim() + '> .'
    }
    if(form.targetObjectsOf != undefined) {
        if(form.targetObjectsOfSubject.value.trim() != '') {
            triples += triples += '<' + form.targetObjectsOfSubject.value.trim() + '> <' + form.targetObjectsOf.value + '> <' + form.ressourceIRI.value.trim() + '> .'
        }
    }
    if(form.targetSubjectsOf != undefined) {
        if(form.targetSubjectsOfObject.value.trim() != '') {
            triples += triples += '<' + form.ressourceIRI.value.trim() + '> <' + form.targetSubjectsOf.value + '> <' + form.targetSubjectsOfObject.value.trim() + '> .'
        }
    }
    var inputs = form.getElementsByTagName('div');
    for (var i = 0; i < inputs.length; i++) {
        var subinputs = inputs[i].getElementsByTagName('div');
        for (var j = 0; j < subinputs.length; j++) {
            var object = subinputs[j].children[0].value.trim();
            if(subinputs[j].children[1].checked){
                object = '<' + object +  '>';
            }
            else {
                object = '"' + object +  '"';
                if(subinputs[j].parentElement.dataset.type != "") {
                    object += "^^" + subinputs[j].parentElement.dataset.type
                }
            }
            triples += '<' + form.ressourceIRI.value.trim() + '> <' + inputs[i].id +
                       '> ' + object + ' . ';
        }
    }
    if(form.namedGraph.value === "") {
        query = "DELETE { <" + form.ressourceIRI.value.trim() + "> ?p ?o} WHERE { <" + form.ressourceIRI.value.trim() + "> ?p ?o . }" +
                "INSERT DATA {" + triples + "}";
    }
    else {
        query = "DELETE { GRAPH <" + form.namedGraph.value.trim() + ">  {<" + form.ressourceIRI.value.trim() + "> ?p ?o}} WHERE { GRAPH <" + form.namedGraph.value.trim() + "> {<" + form.ressourceIRI.value.trim() + "> ?p ?o . }};" +
                "INSERT DATA { GRAPH <" + form.namedGraph.value.trim() + "> {" + triples + "}}";
    }
    var xhttp;
    xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            resultPresentation(this);
        }
    };
    alert(query);
    xhttp.open("POST", form.endpoint.value.trim(), true);
    xhttp.setRequestHeader("Content-Type", "application\/x-www-form-urlencoded");
    xhttp.send("update=" + encodeURIComponent(query));
}

function resultPresentation(result){
    alert(result);
}

function checkFormValidity(subDiv){
    if(subDiv.children[1].checked) {
        var objectUri = new URI(subDiv.children[0].value)
        if(!((objectUri.is("url") || objectUri.is("urn")) && objectUri.is("absolute"))){
            subDiv.children[0].style.background = "red"
            subDiv.dataset.correct = ""
        }
        else{
            subDiv.children[0].style.background = "white"
            subDiv.children[0].title = ""
            subDiv.dataset.correct = "correct"
        }
    }
    else if(subDiv.children[0].value == ""){
        subDiv.children[0].style.background = "red"
        subDiv.dataset.correct = ""
    }
    else if(subDiv.children[0].pattern != '' && subDiv.children[0].pattern != undefined && !subDiv.children[0].checkValidity()) {
        //checks for validity of pattern/xsd type
        subDiv.children[0].style.background = "red"
        subDiv.children[0].title = subDiv.children[0].pattern
        subDiv.dataset.correct = ""
    }
    else {
        //future checks for string length etc.
        subDiv.children[0].style.background = "white"
        subDiv.children[0].title = ""
        subDiv.dataset.correct = "correct"
    }
    checkMainDivValidity(subDiv.parentElement)
}

function checkMainDivValidity(mainDiv){
    var subDivs = mainDiv.getElementsByTagName("div"),
    allSDivsCorrect = true;
    for(var i = 0; i < subDivs.length; i++) {
        if(subDivs[i].dataset.correct == "") {
            allSDivsCorrect = false;
        }
    }
    if(allSDivsCorrect){
        mainDiv.dataset.correct = "correct";
    }
    checkCompleteValidity(mainDiv.parentElement);
}

function checkCompleteValidity(form){
    var mainDivs = form.getElementsByTagName('div'),
    allMDivsCorrect = true;
    for (var i = 0; i < mainDivs.length; i++) {
        if(mainDivs[i].dataset.correct == "") {
            allMDivsCorrect = false;
        }
    }
    if(allMDivsCorrect){
        document.getElementById("submitbutton").disabled = false
    }
    else{
        document.getElementById("submitbutton").disabled = true
    }
}
</script>"""

    propertyMainDiv = """<div id="{}" data-min="{}" data-max="{}" data-type="{}" data-pattern="{}" data-correct="">
{}:<br>"""

    propertySubDiv = """<div id="{id}" data-correct="">
<input type="text" name="{id}" pattern="{pattern}" class='{jsclass}' onkeyup="checkFormValidity(this.parentElement)" onchange="checkFormValidity(this.parentElement)" style="background:red">
<input type="radio" name="{id}radio" {choice} value="iri" onclick="checkFormValidity(this.parentElement)" {0}>IRI
<input type="radio" name="{id}radio" {choice} value="literal" onclick="checkFormValidity(this.parentElement)" {1}>Literal{2}
<button type="button" onclick="textfieldDel('{3}', this.parentElement)">-</button>
<br>
</div>"""

    propertyMainDivClose = """</div>
<button type="button" onclick="textfieldAdd('{}')">+ {}{}</button>"""

    choiceInput = """<input type="radio" name="{}" value="{}"> {}<br>"""

    jqueryCDN = """<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>"""

    datatypeLink = ' (<a href="{datatype}" target="_blank">{datatype}</a>)'
