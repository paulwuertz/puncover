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
