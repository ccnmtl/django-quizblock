function initShowHide() {
	if (document.getElementById && document.getElementsByTagName && document.createTextNode) {
		hideAll();
		var as = document.getElementsByTagName('a');
		for (var i = 0; i < as.length; i++) {
			if (as[i].className == "moretoggle") {
				as[i].onclick = function() {
					show(this);
					return false;
				}
			}
		}			
	}
}

function show(s) {
	var id = s.href.match(/#(\w.+)/)[1];
	document.getElementById(id).style.display = 'block';
	s.innerHTML = "Hide answer &#62;&#62;";
	s.onclick = function () {
		hide(this);
		return false;
	}
}

function hide(s) {
	var id = s.href.match(/#(\w.+)/)[1];
	document.getElementById(id).style.display = 'none';
	s.innerHTML = "Show answer &#62;&#62;";
	s.onclick = function () {
		show(this);
		return false;
	}
}

function hideAll() {
	var divs = document.getElementsByTagName('div');
	for (var i = 0; i < divs.length; i++) {
		if (divs[i].className == "toggleable") {
			divs[i].style.display = 'none';
		}
	}
}

function addLoadEvent(func) {
  	var oldonload = window.onload;
  	if (typeof window.onload != 'function') {
    		window.onload = func;
  	} else {
    		window.onload = function() {
      			oldonload();
      			func();
    		}
  	}
}


addLoadEvent(initShowHide);



function hideAnswers() {
	if (document.getElementById('inlinedisplay')) {
		var divtag = document.getElementsByTagName("div");
		var divlength = divtag.length;
		for (var i=0; i<divlength; i++) {
			var divtagclass = divtag[i].className;	
			if (divtagclass=='answertext') {
				divtag[i].style.display="none";
			}
		}
	}
}

function reveal() {
	if (document.getElementById('inlinedisplay')) {
		var divtag = document.getElementsByTagName("div");
		var divlength = divtag.length;
		for (var i=0; i<divlength; i++) {
			var divtagclass = divtag[i].className;
			if (divtagclass=='answertext') {
				if (divtag[i].style.display=="block") {
					divtag[i].style.display="none";
					document.getElementById("displaytrigger").innerHTML="Show &gt;&gt;";
				}
				else {
					divtag[i].style.display="block";
					document.getElementById("displaytrigger").innerHTML="Hide &gt;&gt;";
				}
			}
		}
	}
}

addLoadEvent(hideAnswers);
