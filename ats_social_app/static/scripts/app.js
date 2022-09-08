const dropdowns = document.querySelectorAll('.aside__dropdown');
const logout = document.getElementById('popup-modal');
const group = document.getElementById('group-action');
const group_modal = document.getElementById('group_section');
const large_modal = document.getElementById('large-modal')

const action_modal = document.querySelector('#group-action');

let currentDropdown = null;
const uls = document.querySelectorAll('.aside__dropdown ul');
const btns = document.querySelectorAll('.aside__dropdown .arrow-down');

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


group?.addEventListener('click', () => {
  large_modal.style.display = 'flex';
});

function closeDialog() {
  large_modal.style.display = "none"

}

group?.addEventListener('click', (e) => {
  if (e.target.id === 'popup-modal') {
    logout.style.display = 'none';
  }
});


