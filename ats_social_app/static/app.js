const dropdowns = document.querySelectorAll('.aside__dropdown');

let currentDropdown = null;
const uls = document.querySelectorAll('.aside__dropdown ul');
const btns = document.querySelectorAll('.aside__dropdown .arrow-down');
console.log(btns);
dropdowns.forEach((dropdown, i) => {
  dropdown.addEventListener('click', (e) => {
    const ul = uls[i];
    const arrow = btns[i];
    e.preventDefault();
    const { value } = dropdown.attributes.getNamedItem('data-index');
    if (currentDropdown !== value) {
      uls.forEach((ul) => {
        ul.style.display = 'none';
      });
      arrow.classList.add('aside__dropdownUpArrow');
      ul.style.display = 'block';
      currentDropdown = value;
    } else {
      ul.style.display = 'none';
      arrow.classList.remove('aside__dropdownUpArrow');
      currentDropdown = null;
    }
  });
});
