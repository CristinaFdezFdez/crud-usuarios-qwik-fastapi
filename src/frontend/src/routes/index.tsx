import { component$ } from "@builder.io/qwik";
import type { DocumentHead } from "@builder.io/qwik-city";
import { UsersList } from "~/components/users-list";

export default component$(() => {
  return (
    <UsersList />
  );
});

export const head: DocumentHead = {
  title: "Alan Turing Bank",
  meta: [
    {
      name: "description",
      content: "Gestión de usuarios de Alan Turing Bank",
    },
  ],
};
