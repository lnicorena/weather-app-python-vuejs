// https://docs.cypress.io/api/introduction/api.html

describe("General tests", () => {
  it("Visits the app main page", () => {
    cy.visit("/");
    cy.get(".address-search-group").contains("show me the current temperature");
    cy.get(".address-search-group input").should("have.text", "");

    let some_address = "R. Dante de Patta, Ingleses, Florianópolis";
    cy.get(".address-search-group input")
      .type(some_address)
      .should("have.value", some_address);
  });

  it("Searches for address and get the temperature", () => {
    cy.visit("/");

    // Get a temperature for an address
    let address1 = "459 Broadway, New York";
    cy.get(".address-search-group input").type(address1);
    cy.get(".address-search-group button").click();

    cy.wait(500);

    // Get a temperature for another address
    let address2 = "515 N. State Street, Chicago";
    cy.get(".address-search-group input")
      .clear()
      .type(address2);
    cy.get(".address-search-group button").click();

    cy.wait(500);
  });

  it("Get temperature by search history", () => {
    cy.visit("/");

    let address1 = "459 Broadway, New York";
    // Get a temperature for this address
    cy.get(".address-search-group input").type(address1.substr(0, 6));
    cy.wait(1000);
    cy.get(".list-group.vbt-autcomplete-list")
      .contains(address1)
      .click();
    cy.wait(500);
  });
});
