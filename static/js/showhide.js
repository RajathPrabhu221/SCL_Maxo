var a=1;
function show_hide(){
    if(a==1){
        document.getElementById('response').style.display="inline";
        document.getElementById('cancel').style.display="inline";
        document.getElementById('submit').style.display="inline";
        document.getElementById('reply').style.display="none";
        return a=0;
    }

    else{
        document.getElementById('response').style.display="none";
        document.getElementById('cancel').style.display="none";
        document.getElementById('submit').style.display="none";
        document.getElementById('reply').style.display="inline";
        return a=1;
    }
}


