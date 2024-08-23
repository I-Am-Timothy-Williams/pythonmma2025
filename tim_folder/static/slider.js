// const rangeInput = document.querySelectorAll(".range-input input"),
// ageInput = document.querySelectorAll(".age-input input"),
// range = document.querySelector(".slider .progress");
// let ageGap = 1;

// ageInput.forEach(input =>{
//     input.addEventListener("input", e =>{
//         let minAge = parseInt(ageInput[0].value),
//         maxAge = parseInt(ageInput[1].value);
        
//         if((maxAge - minAge >= ageGap) && maxAge <= rangeInput[1].max){
//             if(e.target.className === "input-min"){
//                 rangeInput[0].value = minAge;
//                 range.style.left = ((minAge / rangeInput[0].max) * 100) + "%";
//             }else{
//                 rangeInput[1].value = maxAge;
//                 range.style.right = 100 - (maxAge / rangeInput[1].max) * 100 + "%";
//             }
//         }
//     });
// });

