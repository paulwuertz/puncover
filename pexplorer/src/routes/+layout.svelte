<script>
    let { children } = $props();
    import { base } from '$app/paths';
    import { browser } from '$app/environment';
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { Collapse, Nav, Navbar, NavbarBrand, NavItem, NavLink, NavbarToggler } from '@sveltestrap/sveltestrap';
	import { symbols } from './symbols.svelte.js';

    let isOpen = $state(true);

    function handleUpdate(event) {
        isOpen = event.detail.isOpen;
    }

    export async function load({ data }) {
        if (browser) {
            // load elf data
            const hasElfURLData = $page.url.searchParams.has('elfURLData');
            const storedElfURLData = localStorage.getItem("lastOpenElfURL");
            const elfUrl = (hasElfURLData) ? decodeURIComponent($page.url.searchParams.get('elfURLData'))
                                           : storedElfURLData;
            if (elfUrl && Object.keys(symbols.symbols).length == 0) {
                // download data
                const response = await fetch(elfUrl);
                const data = await response.json();
                // persist
                localStorage.lastOpenElfURL = elfUrl;
                localStorage.elfStorageDate = new Date().toISOString();
                symbols.symbols = data;
                console.log("Loaded elf data");
                symbols.elfDataProvided = true;
            }
            // version of the elf
            const hasSelectedVersion = $page.url.searchParams.has('selected_version');
            if (hasSelectedVersion) {
                const selected_version_param = $page.url.searchParams.get('selected_version')
                localStorage.selected_version = selected_version_param;
                symbols.selected_version = selected_version_param;
            } else if (localStorage.getItem("selected_version")) {
                symbols.selected_version = localStorage.getItem("selected_version");
            }
            // version of the elf to compare to
            const hasSelectedVersionToCompare = $page.url.searchParams.has('symbols.selected_versions_to_compare');
            if (hasSelectedVersionToCompare) {
                const selected_version_to_compare_param = $page.url.searchParams.get('symbols.selected_versions_to_compare')
                localStorage.selected_versions_to_compare = selected_version_to_compare_param;
                symbols.selected_versions_to_compare = selected_version_to_compare_param;
            } else if (localStorage.getItem("selected_versions_to_compare")) {
                symbols.selected_versions_to_compare = localStorage.getItem("selected_versions_to_compare");
            }
            // localstorage has 5-10 MB max so split TODO test compression...
            // let versions = Object.keys(data);
            // localStorage.elfVersions = versions;
            // for (const version of versions) {
            //     localStorage[version] = JSON.stringify(data[version]);
            // }
            // else if (localStorage.getItem("elfURLData")) {
            //     alert("elfURLData found in storage"+localStorage.getItem("elfURLData"))
            //     elfDataProvided = false;
            // }
        }
    };
</script>

<nav>
  <Navbar color="light" light expand="md" container="md">
    <NavbarBrand href="{base}/">Puncover</NavbarBrand>
    <NavbarToggler on:click={() => (isOpen = !isOpen)} />
    <Collapse {isOpen} navbar expand="md" on:update={handleUpdate}>
        <Nav class="ms-auto" navbar>
            <NavItem><NavLink href="{base}/symbols">Symbols</NavLink></NavItem>
            <NavItem><NavLink href="{base}/threads">Thread (TODO)</NavLink></NavItem>
            <NavItem><NavLink href="{base}/interrupts">Interrupts (TODO)</NavLink></NavItem>
            <NavItem><NavLink href="{base}/">Compare Versions</NavLink></NavItem>
            <NavItem><NavLink href="{base}/settings">Settings (TODO)</NavLink></NavItem>
            <NavItem><NavLink href="{base}/about">About</NavLink></NavItem>
        </Nav>
    </Collapse>
  </Navbar>
  <!--- TODO add breadcrumbs-->
</nav>

{@render children()}
