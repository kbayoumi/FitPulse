document.addEventListener("DOMContentLoaded", function() {
    const rankPic = document.getElementById("rank-pic");
    const ranksModal = document.getElementById("ranksModal");
    const closeModal = document.getElementById("closeModal");

    // Show modal on rank-pic click
    rankPic.addEventListener("click", function() {
        ranksModal.style.display = "flex"; // Show modal as flex
    });

    // Close modal when close button is clicked
    closeModal.addEventListener("click", function() {
        ranksModal.style.display = "none"; // Hide modal
    });

    // Close modal when clicking outside of the modal content
    window.addEventListener("click", function(event) {
        if (event.target === ranksModal) {
            ranksModal.style.display = "none"; // Hide modal
        }
    });
});
