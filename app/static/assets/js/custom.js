$(document).ready(function(){

    $("#teamsLink").hover(
        function(){
            $("#teamsLink").dropdown('toggle');
        },
        function(){}
    )

    $("#teamsDrop").mouseleave(function(){
        $("#teamsLink").dropdown('toggle');
    })

    $("#profileLink").hover(
        function(){
            $(this).dropdown('toggle');},
        function(){}
    )

    $("#profileDrop").mouseleave(function(){
        $("#profileLink").dropdown('toggle');
    })
    
    $('#positionFilter').hover(
        function() {
            $(this).addClass('focus');},
        function() {
            $(this).removeClass('focus');}
    );

    $('#weekSelect').on('change', function() {
        document.forms['weekForm'].submit();
     });

     $("#tabs").tabs();

     $("tbody").sortable({
         items: "> tr",
         appendTo: "parent",
         helper: "clone"
     }).disableSelection();
 
     $("#tabs ul li a").droppable({
         hoverClass: "drophover",
         tolerance: "pointer",
         drop: function(e, ui) {
             var tabdiv = $(this).attr("href");
             $(tabdiv + " table tr:last").after("<tr>" + ui.draggable.html() + "</tr>");
             ui.draggable.remove();
         }
     });

    addFileName(document.getElementById('customFile'));

    
    
});

window.onload = function() {
    var links = window.location.href.split('/');
    if (links.includes('home') || links.includes('home#'))
    {
        document.getElementById('homeLink').classList.add('active');
    }
    if (links.includes('matchups') || links.includes('matchups#'))
    {
        document.getElementById('matchupsLink').classList.add('active');
    }
    if (links.includes('standings') || links.includes('standings#'))
    {
        document.getElementById('standingsLink').classList.add('active');
    }
    if (links.includes('feed') || links.includes('feed#'))
    {
        document.getElementById('feedLink').classList.add('active');
    }
    if (links.includes('players') || links.includes('players#'))
    {
        document.getElementById('playersLink').classList.add('active');
    }
    if (links.includes('teams') || links.includes('teams#'))
    {
        document.getElementById('teamsLink').classList.add('active');
    }
    if (links.includes('purse') || links.includes('purse#'))
    {
        document.getElementById('purseLink').classList.add('active');
    }

}
function addFileName(cfile) {
    cfile.addEventListener('change', function () {
        document.getElementById('customFileLabel').innerText = event.srcElement.files[0].name;
    });
}

function changeImage(elem_id, post_id){
    var counter = parseInt(document.getElementById(elem_id.concat('p')).innerText);
    if (document.getElementById(elem_id).src == "http://127.0.0.1:5000/static/images/like.png")
    {
      document.getElementById(elem_id).src = "/static/images/unlike.png";
      document.getElementById(elem_id.concat('p')).innerText = counter + 1;
      sendLike(post_id,'1');
    }
    else
    {
      document.getElementById(elem_id).src = "/static/images/like.png";
      document.getElementById(elem_id.concat('p')).innerText = counter - 1;
      sendLike(post_id,'0');
    }
}

function sendLike(id, action) {
    var jqXHR = $.ajax({
        type: "POST",
        url: "/like",
        async: true,
        data: { id: id, action: action }
    });
    return jqXHR.responseText;
}

function watchListChange(elem_id){
    if(document.getElementById(elem_id).src == "http://127.0.0.1:5000/static/images/star_outline.png")
    {
        document.getElementById(elem_id).src = "/static/images/star.png";
        watchListAction(1, elem_id.split('_')[1]);
    }
    else
    {
        document.getElementById(elem_id).src = "/static/images/star_outline.png";
        watchListAction(0, elem_id.split('_')[1]);
    }
}
function watchListAction(action, id){
    var jqXHR = $.ajax({
        type: "POST",
        url: "/league/watchlist",
        async: true,
        data: { id: id, action: action }
    });
    return jqXHR.responseText;
}

function deleteComment(commentid, postid, uid, postuid){
    var counter = parseInt(document.getElementById(postuid.concat('cc')).innerText);
    document.getElementById(postuid.concat('cc')).innerText = counter - 1;
    document.getElementById(uid).remove();
    var jqXHR = $.ajax({
        type: "POST",
        url: "/delete_comment",
        async: true,
        data: { postid: postid, commentid: commentid }
    });
    return jqXHR.responseText;
}

function collapse()
{
    $('.collapse').collapse('hide');
}

function collapseOne(elem_id)
{
    $('#'+ elem_id).collapse('hide');
}

function initSliders() {
    var slide = $('.noUi-origin');
    var position = slide.position();
    var percent = parseFloat(position.left) / 390;
    alert(percent);
}

$(function () {
    $('.selectpicker').selectpicker();
});

function paginate()
{
    var recordPerPage = 25;
    if(($('#pagedTable').find('tbody tr:has(td)').length / recordPerPage) > 9)
    {
        recordPerPage = Math.ceil($('#pagedTable').find('tbody tr:has(td)').length/10);
    }
    var totalPages = Math.ceil($('#pagedTable').find('tbody tr:has(td)').length / recordPerPage);
    var $pages = $('<ul class="pagination justify-content-center"></ul>');
    for (i = 0; i < totalPages; i++) {
        $('<li class="page-item"><a class="page-link" href="#">&nbsp;' + (i + 1) + '</a></li>').appendTo($pages);
    }
    $pages.appendTo('#playersPage');

    $('.page-link').hover(
        function() {
            $(this).addClass('focus');},
        function() {
            $(this).removeClass('focus');}
    );

    $('table').find('tbody tr:has(td)').hide();
    var tr = $('table tbody tr:has(td)');
    for (var i = 0; i <= recordPerPage - 1; i++) {
        $(tr[i]).show();
    }
   
    $('.page-link').click(function(event) {
        $('#pagedTable').find('tbody tr:has(td)').hide();
        for (var i = ($(this).text() - 1) * recordPerPage; i <= $(this).text() * recordPerPage - 1; i++) {
            $(tr[i]).show();}
    });
}
function enableButton(btn_id, select_id, selected, txt){
    if(document.getElementById(btn_id).disabled == true)
    {
        document.getElementById(btn_id).disabled = false;
    }
    resetSelect(select_id, selected, txt);
}

function resetSelect(select_id, selected, txt)
{
    if(selected == '--Clear--')
    {
        var selectBox = $("#" + select_id)[0];
        var option = document.createElement("option");
        option.value = '';
        option.text = txt;
        selectBox.options[0] = option;
        option.selected = true;
    }
    if(selected == 'Current')
    {
        var selectBox = $("#" + select_id)[0];
        var option = document.createElement("option");
        option.value = txt;
        option.text = txt;
        selectBox.options[0] = option;
        option.selected = true;
    }
}

function clearFilters()
{
    var selectPosition = $('#positionFilter')[0];
    var selectTeam = $('#teamFilter')[0];
    var playerFilter = $('#playerFilter');
    var postionOption = document.createElement("option");
    var teamOption = document.createElement("option");
    postionOption.value = "";
    postionOption.text = 'Position';
    selectPosition.options[0] = postionOption;
    postionOption.selected = true;
    teamOption.value = "";
    teamOption.text = 'Team';
    selectTeam.options[0] = teamOption;
    teamOption.selected = true;
    playerFilter.val("");
    
}

function getWatchlist(){
    $("#playerSearchForm").submit();
}