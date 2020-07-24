
(function(){
	"user-strict"
	document.getElementById('DOMContentLoaded', function(argument) {
		let t = document.getElementById('time');

		setInterval(updateTime, 1000);

		function updateTime(){
			let d = new Date();
			
			let hours = d.getHours();
			if (hours > 12){
				hours -= 12;
			}

			t.innerHTML = hours +":" + getMinutes() + ":" + d.getSeconds();
		}
	});

});
