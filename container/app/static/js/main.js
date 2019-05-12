jQuery.fn.cleanWhitespace = function() {
    this.contents().filter(
        function() { return (this.nodeType == 3 && !/\S/.test(this.nodeValue)); })
        .remove();
    return this;
}

function appendingAnsers(questions) {
    questions.forEach(function(question) {
	let answered = " ";
	if (question.accepted == 1) {
	     answered = " answered ";
	}
	let dom = `<div class="answer${answered}result w-100">
	<div class="_header d-flex">
	    <div class="votes">
		<p>${question.votes}</p>
	    </div>
	    `;

	if (question.accepted == 1) {
	    dom += `
	    <div class="accepted">
		<p>Accepted</p>
	    </div>
	    `;
	}
	dom += '</div><div class="answer_code">';
	question.answer.forEach(function(a) {
	    check_if_newline = /\r|\n/.exec(a)

	    if (check_if_newline) {
	    dom += `<pre><code>${a}</code></pre>`
	    }
	});
	dom += `
	</div>
	<div class="_footer d-flex">
	    <div class="author">
		<p>Author: </p>
		<a href='#'>${question.author}</a>
	    </div>
	    <div class="source">
		<p>Source: </p>
		<a href='${question.url}'>${question.source}</a>
	    </div>
	</div>
    </div>
	`
	if (question.accepted == 1) {
	    $(".results").prepend(dom);
	}
	else {
	    $(".results").append(dom);
	}


    }
    )
}
function appendingQuestions(questions) {
    questions.forEach(function(question) {
	let answered = " ";
	if (question.answered == 1) {
	     answered = " answered ";
	}
	let dom = `<div class="question${answered}result w-100">
	<div class="_header d-flex">
	    <div class="votes">
		<p>${question.votes}</p>
	    </div>
	    <div class="title">
		<a href='/${question.question_id}/${encodeURIComponent(question.title)}' target='_blank'>${question.title}</a>
	    </div>
	    `;

	if (question.answered == 1) {
	    dom += `
	    <div class="accepted">
		<p>Answered</p>
	    </div>
	    `;
	}
	dom += `</div><div class="_footer d-flex">
	    <div class="author">
		<p>Answers: </p>
		<p><strong>${question.answers_num}</strong></p>
	    </div>
	    <div class="source">
		<p>Source: </p>
		<a href='${question.url}'>${question.source}</a>
	    </div>
	</div>
    </div>
	`
	if (question.accepted == 1) {
	    $(".results").prepend(dom);
	}
	else {
	    $(".results").append(dom);
	}


    }
    )
}

$( document ).ready(function() {
    hljs.initHighlightingOnLoad();
    // var test_json;
// $(".question pre").each(function(){
//     $(this).html($(this).html().trim());
//   });

    $(".askForm form").submit(function(e) {

	e.preventDefault(); // avoid to execute the actual submit of the form.
	$(".results").html("");
	var form = $(this);
	var url = form.attr('action');

	$.ajax({
	    type: "POST",
	    url: url,
	    data: form.serialize(), // serializes the form's elements.
	    success: function(questions)
	    {
		appendingQuestions(questions);
		document.querySelectorAll('pre code').forEach((block) => {
		    hljs.highlightBlock(block);
		});
	    }
	});
    })
})
