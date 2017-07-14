var mdns = require('multicast-dns')({loopback: true}) 
//might want to move to the mdns package at somepoint - seems more full featured 

 mdns.on('response', function(response) {
 	console.log("got a response\n")
 	response.answers.forEach(function check(answer){
 		if (answer.name.includes("opentrons") || answer.name.includes("ot")){
 			console.log(answer.name)
 			console.log(answer.data)
 		}
 	})
 	response.additionals.forEach(function check(answer){
 		if (answer.name.includes("opentrons") || answer.name.includes("ot")){
 			console.log(answer.name)
 			console.log(answer.data)
		}
	})
})


