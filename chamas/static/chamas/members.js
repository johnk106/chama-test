document.addEventListener('DOMContentLoaded', function () {
    var contributionHeader = document.getElementById('contribution-header');
    var contributionDiv = document.getElementById('member-contributions');

    contributionHeader.addEventListener('click', function () {
      if (contributionDiv.style.display === 'none') {
        contributionDiv.style.display = 'block';
      } else {
        contributionDiv.style.display = 'none';
      }
    });
    var loanHeader = document.getElementById('loan-header');
    var loanDiv = document.getElementById('member-loans');

   loanHeader.addEventListener('click',function (){
    if (loanDiv.style.display === 'none'){
        loanDiv.style.display = 'block';

    }else{
        loanDiv.style.display = 'none'
    }
   })

   var fineHeader = document.getElementById('fine-header');
    var fineDiv = document.getElementById('member-fines');

   fineHeader.addEventListener('click',function (){
    if (fineDiv.style.display === 'none'){
        fineDiv.style.display = 'block';

    }else{
        fineDiv.style.display = 'none'
    }
   })


  });


