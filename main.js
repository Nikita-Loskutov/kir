let miniblob = document.getElementById('miniblob')
function getXY(){
    if (window.scrollY > 280) {
        let winHeight = window.innerHeight
        let blobY = window.scrollY + winHeight/3
        console.log(blobY)
        miniblob.style.display = "block"
        miniblob.style.top = String(blobY)+'px'
    }
    else{
        miniblob.style.display = "none"
    }
}



window.addEventListener('scroll', getXY)


