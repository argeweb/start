function json_async(url,data,successCallback,errorCallback){$.ajax({url:url,type:"POST",cache: false,dataType:"json",data:data,async:1,success:function(a){successCallback(a)},error:function(b,c,d){void 0==errorCallback?alert(d.message):errorCallback(d.message)}})};

jQuery(document).ready(function($) {
    $('body').scrollspy({ target: '#header', offset: 400});
    $(window).bind('scroll', function() {
         if ($(window).scrollTop() > 50) {
             $('#header').addClass('navbar-fixed-top');
         }
         else {
             $('#header').removeClass('navbar-fixed-top');
         }
    });
    $('a.scrollto').on('click', function(e){
        var target = this.hash;
        e.preventDefault();
		$('body').scrollTo(target, 800, {offset: -70, 'axis':'y', easing:'easeOutQuad'});
		if ($('.navbar-collapse').hasClass('in')){
			$('.navbar-collapse').removeClass('in').addClass('collapse');
		}
	});
    json_async("/sysinfo", null, function (data) {
        $("#server_name").text(data.server_name);
        $("#namespace").text(data.namespace);
        $("#theme").text(data.theme);
    });
});

