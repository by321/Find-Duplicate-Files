"use strict";

eel.expose(prompt_alerts);
function prompt_alerts(description) { alert(description); }


function GetDuplicateFiles_callback(n) {
    //alert("GetDuplicateFiles_callback");
    let dupfiles = JSON.parse(n);

    //see .html file for these templates
    let group_template = document.getElementById("group_template");
    let file_template = document.getElementById("file_template");

    let main_div=document.getElementById("main-div");
    for (let i=0;i<dupfiles.length;i++) {
        let group=dupfiles[i];
        let t= group_template.content.cloneNode(true);
        t.firstElementChild.firstElementChild.innerText='group '+i.toString()+': file length='+group.length.toString()+" MD5="+group.md5_hash;
        //console.log("*** "+group.length.toString()+" "+group.md5_hash)
        for (let j=0;j<group.filenames.length;j++) {
            //console.log("    "+group.filenames[j]);
            let t2=file_template.content.cloneNode(true);
            t2.children[1].children[1].innerText=group.filenames[j];
            t.firstElementChild.appendChild(t2);
        }
        main_div.appendChild(t);
    }
}

function docBodyClickHandler(evt) {
    console.log("clicked "+ evt.target.className);
    if (evt.target.className === 'open-file-btn') {
        let fn=evt.target.nextElementSibling.childNodes[1].innerText;
        console.log("opening "+fn+" ...");
        eel.OpenFileWithDefaultApp(fn)(function(){});
        //alert(evt.target.nextElementSibling.childNodes[1].innerText);
    } else if (evt.target.className === "select-file-checkbox") {
        //checkbox clicked
    }
}

function clearSelection() {
    const inputs = document.getElementById("main-div").querySelectorAll("input[type='checkbox']:checked");
    if (inputs.length==0) { alert("No file selected."); return; }

    inputs.forEach((inp) => { inp.checked=false });
}

function deleteSelection() {
    document.body.style.cursor = 'wait';
    const inputs = document.getElementById("main-div").querySelectorAll("input[type='checkbox']:checked");
    document.body.style.cursor = 'default';
    if (inputs.length==0) { alert("No file selected."); return; }

    let confirmstr="Please confirm you want to delete "+inputs.length.toString()+ " selected file(s)."
    if (false==confirm(confirmstr)) return;

    document.body.style.cursor = 'wait';
    let fns=[];
    inputs.forEach((inp) => {
        fns.push(inp.nextElementSibling.innerText);
        let p=inp.parentElement; //this is the <label> element
        let pp=p.parentElement; //this is the <fieldset> element
        p.nextElementSibling.remove();
        p.previousElementSibling.remove();
        p.remove();
        if (pp.children.length<2) pp.remove();
        });
    document.body.style.cursor = 'default';
    //alert(fns);
    eel.DeleteSelectedFiles(fns)(function(){});
}

window.onload = function () {
    document.body.addEventListener('click', docBodyClickHandler, false);
    document.getElementById("clear-selection-btn").addEventListener("click", clearSelection);
    document.getElementById("delete-selection-btn").addEventListener("click", deleteSelection);
    eel.GetDuplicateFiles()(GetDuplicateFiles_callback);
}
